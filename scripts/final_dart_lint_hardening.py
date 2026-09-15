from pathlib import Path

# Final pass over every generated Dart source. The upgrade scripts generate code
# dynamically, so this deliberately runs after all feature generators.
ROOT = Path('lib')


def mask_non_code(source):
    out = list(source)
    i = 0
    n = len(source)
    state = 'code'
    quote = ''
    while i < n:
        if state == 'code':
            if source.startswith('//', i):
                out[i] = out[i + 1] = ' '
                i += 2
                state = 'line_comment'
                continue
            if source.startswith('/*', i):
                out[i] = out[i + 1] = ' '
                i += 2
                state = 'block_comment'
                continue
            if source.startswith("'''", i) or source.startswith('"""', i):
                quote = source[i:i + 3]
                out[i:i + 3] = [' '] * 3
                i += 3
                state = 'string'
                continue
            if source[i] in "'\"":
                quote = source[i]
                out[i] = ' '
                i += 1
                state = 'string'
                continue
            i += 1
            continue
        if state == 'line_comment':
            if source[i] == '\n':
                state = 'code'
            else:
                out[i] = ' '
            i += 1
            continue
        if state == 'block_comment':
            if source.startswith('*/', i):
                out[i] = out[i + 1] = ' '
                i += 2
                state = 'code'
            else:
                if source[i] != '\n':
                    out[i] = ' '
                i += 1
            continue
        if len(quote) == 3 and source.startswith(quote, i):
            out[i:i + 3] = [' '] * 3
            i += 3
            state = 'code'
            continue
        if len(quote) == 1 and source[i] == '\\':
            out[i] = ' '
            if i + 1 < n and source[i + 1] != '\n':
                out[i + 1] = ' '
                i += 2
            else:
                i += 1
            continue
        if len(quote) == 1 and source[i] == quote:
            out[i] = ' '
            i += 1
            state = 'code'
            continue
        if source[i] != '\n':
            out[i] = ' '
        i += 1
    return ''.join(out)


def matching_paren(masked, opening):
    depth = 0
    for i in range(opening, len(masked)):
        if masked[i] == '(':
            depth += 1
        elif masked[i] == ')':
            depth -= 1
            if depth == 0:
                return i
    return None


def find_single_statement_ifs(source):
    masked = mask_non_code(source)
    matches = []
    i = 0
    while i < len(masked) - 1:
        if masked.startswith('if', i) and (i == 0 or not (masked[i - 1].isalnum() or masked[i - 1] == '_')) and not (i + 2 < len(masked) and (masked[i + 2].isalnum() or masked[i + 2] == '_')):
            j = i + 2
            while j < len(masked) and masked[j].isspace():
                j += 1
            if j < len(masked) and masked[j] == '(':
                close = matching_paren(masked, j)
                if close is not None:
                    body = close + 1
                    while body < len(masked) and masked[body].isspace():
                        body += 1
                    if body < len(masked) and masked[body] != '{':
                        # This lint rule concerns a single executable statement;
                        # semicolon is a safe boundary for return/continue/break
                        # and ordinary assignment/expression statements.
                        semi = masked.find(';', body)
                        if semi >= 0:
                            matches.append((i, body, semi + 1))
                            i = semi + 1
                            continue
        i += 1
    return matches


def expand(source):
    matches = find_single_statement_ifs(source)
    if not matches:
        return source, 0
    result = source
    for start, body, end in reversed(matches):
        condition_end = body
        while condition_end > start and result[condition_end - 1].isspace():
            condition_end -= 1
        condition = result[start:condition_end]
        statement = result[body:end]
        line_start = result.rfind('\n', 0, start) + 1
        indent = result[line_start:start]
        if indent.strip():
            indent = ''
        result = result[:start] + condition + '{\n' + indent + '  ' + statement.strip() + '\n' + indent + '}' + result[end:]
    return result, len(matches)


changed_files = 0
changed_statements = 0
for path in sorted(ROOT.rglob('*.dart')):
    text = path.read_text(encoding='utf-8')
    for _ in range(20):
        new_text, changed = expand(text)
        text = new_text
        changed_statements += changed
        if changed == 0:
            break
    else:
        raise SystemExit(f'Lint hardening exceeded rewrite safety limit in {path}')
    remaining = find_single_statement_ifs(text)
    if remaining:
        lines = ', '.join(str(text.count('\n', 0, start) + 1) for start, _, _ in remaining[:12])
        raise SystemExit(f'Final Dart lint hardening failed in {path} at line(s): {lines}')
    if text != path.read_text(encoding='utf-8'):
        path.write_text(text, encoding='utf-8')
        changed_files += 1

print(f'Final Dart lint hardening passed across lib: {changed_files} file(s), {changed_statements} flow statement(s) normalized.')
