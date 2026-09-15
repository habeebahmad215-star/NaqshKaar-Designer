from pathlib import Path
import re

# All feature-upgrade scripts mutate the generated controller in sequence.
# Do the final style normalization only after every mutation has run, so a
# later generator cannot re-introduce curly_braces_in_flow_control_structures.
path = Path('lib/state/workspace_controller.dart')
text = path.read_text(encoding='utf-8')

# Normalize whole-line single-statement if guards.  Restricting this pass to
# complete source lines avoids touching strings, comments, or collection-if
# expressions.  The statement forms are exactly those reported by the
# flutter_lints rule and the ones used by the generators in this project.
pattern = re.compile(r'^(?P<indent>\s*)if\s*\((?P<condition>.*)\)\s*(?P<statement>return|continue|break)\s*;\s*$', re.MULTILINE)

def expand(match):
    indent = match.group('indent')
    condition = match.group('condition').strip()
    statement = match.group('statement')
    return f'{indent}if ({condition}) {{\n{indent}  {statement};\n{indent}}}'

previous = None
while previous != text:
    previous = text
    text = pattern.sub(expand, text)

# Verification: after normalization there must be no whole-line single-
# statement control-flow guards left in the generated controller.
remaining = list(pattern.finditer(text))
if remaining:
    lines = ', '.join(str(text.count('\n', 0, m.start()) + 1) for m in remaining[:10])
    raise SystemExit(f'Final Dart lint hardening verification failed at line(s): {lines}')

path.write_text(text, encoding='utf-8')
print('Final Dart lint hardening passed: no single-line if return/continue/break guards remain.')
