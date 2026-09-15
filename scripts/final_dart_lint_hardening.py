from pathlib import Path
import re

ROOT = Path('lib')

# Only rewrite a complete, single-line `if (...) statement;` construct.
# This intentionally avoids parsing/rebuilding multiline Dart syntax: generated
# collection-if, callbacks, else-if chains, and multiline expressions must be
# left untouched. The controller-specific generator handles its own assignments.
SIMPLE_IF = re.compile(
    r'^(?P<indent>\s*)if\s*\((?P<condition>.+)\)\s+(?P<statement>(?!\{)(?:[^{};]|\{[^{}]*\})+;)\s*$'
)


def normalize_line(line):
    match = SIMPLE_IF.match(line)
    if not match:
        return line, False
    indent = match.group('indent')
    condition = match.group('condition').strip()
    statement = match.group('statement').strip()
    # Avoid constructs where a trailing else would change binding semantics.
    if re.search(r'\}\s*else\b', statement):
        return line, False
    return f'{indent}if ({condition}) {{\n{indent}  {statement}\n{indent}}}', True


changed_files = 0
changed_statements = 0
for path in sorted(ROOT.rglob('*.dart')):
    original = path.read_text(encoding='utf-8')
    lines = original.splitlines(keepends=True)
    output = []
    changed = False
    for line in lines:
        normalized, did_change = normalize_line(line.rstrip('\n'))
        if did_change:
            output.append(normalized + '\n')
            changed_statements += 1
            changed = True
        else:
            output.append(line)
    text = ''.join(output)
    if changed:
        path.write_text(text, encoding='utf-8')
        changed_files += 1

print(f'Syntax-safe Dart lint hardening: {changed_files} file(s), {changed_statements} simple flow statement(s) normalized.')
