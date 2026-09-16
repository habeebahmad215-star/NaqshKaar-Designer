from pathlib import Path
import re

workspace = Path('lib/screens/workspace_screen.dart')
canvas = Path('lib/widgets/design_canvas.dart')

# The preview painter belongs to the workspace gallery, not the canvas widget.
# Move it after the border generator has inserted it, then keep the canvas focused
# only on the runtime border painter.
canvas_text = canvas.read_text(encoding='utf-8')
match = re.search(r'class _BorderPreviewPainter extends CustomPainter \{.*?\n\}\n\nclass _SelectionBorderPainter extends CustomPainter \{', canvas_text, flags=re.S)
if match:
    preview = match.group(0)
    preview_class = preview[:preview.rfind('\n\nclass _SelectionBorderPainter')]
    canvas_text = preview.replace(preview_class + '\n\n', '')
    canvas.write_text(canvas_text, encoding='utf-8')
    workspace_text = workspace.read_text(encoding='utf-8')
    if '_BorderPreviewPainter extends CustomPainter' not in workspace_text:
        anchor = '  Widget _viewButton(IconData icon, String tooltip, VoidCallback onTap) {'
        if anchor not in workspace_text:
            raise SystemExit('Border compile integration: workspace insertion anchor missing')
        workspace_text = workspace_text.replace(anchor, preview_class + '\n\n' + anchor, 1)
    workspace_text = workspace_text.replace("import 'dart:math' as math;\n", '', 1)
    workspace.write_text(workspace_text, encoding='utf-8')

# Normalize numeric literals for APIs that require doubles and fix two helper
# methods that were accidentally referring to the painter's old variable name.
canvas_text = canvas.read_text(encoding='utf-8')
start = canvas_text.find('class _ReadyBorderPainter extends CustomPainter {')
end = canvas_text.find('class _SelectionBorderPainter extends CustomPainter {')
if start >= 0 and end > start:
    head = canvas_text[:start]
    border = canvas_text[start:end]
    tail = canvas_text[end:]
    border = border.replace('math.max(1, ', 'math.max(1.0, ')
    border = border.replace('canvas.drawRRect', 'c.drawRRect')
    border = border.replace('canvas.save()', 'c.save()')
    border = border.replace('canvas.clipRect', 'c.clipRect')
    border = border.replace('canvas.drawPath', 'c.drawPath')
    border = border.replace('canvas.restore()', 'c.restore()')
    canvas.write_text(head + border + tail, encoding='utf-8')

print('Border compile integration finalized cleanly')
