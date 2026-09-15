from pathlib import Path
import re

path = Path('lib/state/workspace_controller.dart')
text = path.read_text(encoding='utf-8')

# Normalize every simple element-field assignment used as an unbraced if body.
pattern = re.compile(r'if\s*\((?P<condition>[^()\n]+)\)\s*(?P<statement>e\.[A-Za-z_][A-Za-z0-9_]*\s*=\s*[^;\n]+;)')

def replace(match):
    return f"if ({match.group('condition').strip()}) {{\n      {match.group('statement').strip()}\n    }}"

previous = None
while previous != text:
    previous = text
    text = pattern.sub(replace, text)

remaining = list(pattern.finditer(text))
if remaining:
    lines = ', '.join(str(text.count('\n', 0, m.start()) + 1) for m in remaining[:12])
    raise SystemExit('Controller inline assignment verification failed at line(s): ' + lines)

path.write_text(text, encoding='utf-8')
print('All generated element-field inline if assignments normalized successfully.')
