from pathlib import Path

# Safety pass after the UX generator: resolve cross-file method/type contracts
# before dart fix/format/analyze.

p = Path('lib/screens/workspace_screen.dart')
s = p.read_text(encoding='utf-8')
if 'Future<void> _layersSheet() async' not in s:
    marker = "  Widget _viewButton(IconData icon, String tooltip, VoidCallback onTap) {"
    method = '''  Future<void> _layersSheet() async {\n    await showModalBottomSheet<void>(\n      context: context,\n      isScrollControlled: true,\n      showDragHandle: true,\n      builder: (_) => SizedBox(\n        height: MediaQuery.sizeOf(context).height * .78,\n        child: LayersPanel(controller: controller),\n      ),\n    );\n  }\n\n'''
    if marker not in s:
        raise SystemExit('Workspace view-button anchor not found')
    s = s.replace(marker, method + marker, 1)
p.write_text(s, encoding='utf-8')

p = Path('lib/widgets/layers_panel.dart')
s = p.read_text(encoding='utf-8')
s = s.replace(
    'final index = element.shapeType.clamp(0, PremiumShapeCatalog.borderNames.length - 1);',
    'final index = element.shapeType.clamp(0, PremiumShapeCatalog.borderNames.length - 1).toInt();',
)
s = s.replace(
    'final index = element.shapeType.clamp(0, PremiumShapeCatalog.shapeNames.length - 1);',
    'final index = element.shapeType.clamp(0, PremiumShapeCatalog.shapeNames.length - 1).toInt();',
)
p.write_text(s, encoding='utf-8')

# Fail fast if the two most important cross-file contracts are absent.
ws = Path('lib/screens/workspace_screen.dart').read_text(encoding='utf-8')
layers = Path('lib/widgets/layers_panel.dart').read_text(encoding='utf-8')
if 'Future<void> _layersSheet() async' not in ws:
    raise SystemExit('Layers top-toolbar action has no sheet implementation')
if 'PremiumShapeCatalog.borderNames[index]' not in layers:
    raise SystemExit('Border layer label was not generated')
if '.clamp(0, PremiumShapeCatalog.borderNames.length - 1).toInt()' not in layers:
    raise SystemExit('Border layer index is not normalized to int')
print('Final editor UX safety contracts verified.')
