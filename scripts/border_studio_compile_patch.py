from pathlib import Path

workspace = Path('lib/screens/workspace_screen.dart')
text = workspace.read_text(encoding='utf-8')
if "import 'dart:math' as math;" not in text:
    text = "import 'dart:math' as math;\n" + text
workspace.write_text(text, encoding='utf-8')

canvas = Path('lib/widgets/design_canvas.dart')
text = canvas.read_text(encoding='utf-8')
text = text.replace('math.max(1, normal.distance)', 'math.max(1.0, normal.distance)')
canvas.write_text(text, encoding='utf-8')
print('Border compile integration finalized')
