from pathlib import Path

ROOT = Path('lib')


def find_condition_end(line, start):
    depth = 0
    quote = None
    escaped = False
    for i in range(start, len(line)):
        ch = line[i]
        if quote is not None:
            if escaped:
                escaped = False
            elif ch == '\\':
                escaped = True
            elif ch == quote:
                quote = None
            continue
        if ch in ('\"', "'"):
            quote = ch
        elif ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
            if depth == 0:
                return i
    return -1


def normalize_line(line):
    stripped = line.lstrip()
    indent = line[:len(line) - len(stripped)]
    if not stripped.startswith('if'):
        return line, False
    if len(stripped) <= 2 or not stripped[2].isspace() and stripped[2] != '(':
        return line, False

    open_paren = stripped.find('(')
    if open_paren < 0:
        return line, False
    close_paren = find_condition_end(stripped, open_paren)
    if close_paren < 0:
        return line, False

    condition = stripped[open_paren + 1:close_paren].strip()
    statement = stripped[close_paren + 1:].strip()
    if not condition or not statement:
        return line, False
    if statement.startswith('{') or statement.startswith('else'):
        return line, False
    if not statement.endswith(';'):
        return line, False
    # Only handle exactly one simple statement. This avoids touching callbacks,
    # collection-if syntax, multiline constructs, or nested control flow.
    if statement.count(';') != 1:
        return line, False

    return (
        f'{indent}if ({condition}) {{\n'
        f'{indent}  {statement}\n'
        f'{indent}}}',
        True,
    )


changed_files = 0
changed_statements = 0
for path in sorted(ROOT.rglob('*.dart')):
    original = path.read_text(encoding='utf-8')
    output = []
    changed = False
    for line in original.splitlines(keepends=True):
        body = line.rstrip('\r\n')
        normalized, did_change = normalize_line(body)
        if did_change:
            output.append(normalized + '\n')
            changed_statements += 1
            changed = True
        else:
            output.append(line)
    if changed:
        path.write_text(''.join(output), encoding='utf-8')
        changed_files += 1

print(
    f'Syntax-safe Dart lint hardening: {changed_files} file(s), '
    f'{changed_statements} simple flow statement(s) normalized.'
)
