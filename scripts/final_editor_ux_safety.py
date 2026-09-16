from pathlib import Path

# Final cross-file safety pass before analyzer.

p = Path('lib/screens/workspace_screen.dart')
s = p.read_text(encoding='utf-8')
if 'Future<void> _layersSheet() async' not in s:
    marker = "  Widget _viewButton(IconData icon, String tooltip, VoidCallback onTap) {"
    method = '''  Future<void> _layersSheet() async {\n    await showModalBottomSheet<void>(\n      context: context,\n      isScrollControlled: true,\n      showDragHandle: true,\n      builder: (_) => SizedBox(\n        height: MediaQuery.sizeOf(context).height * .78,\n        child: LayersPanel(controller: controller),\n      ),\n    );\n  }\n\n'''
    if marker not in s:
        raise SystemExit('Workspace view-button anchor not found')
    s = s.replace(marker, method + marker, 1)

# The font is applied at tile tap time; no result variable is needed.
s = s.replace('final family = await showModalBottomSheet<String>(', 'await showModalBottomSheet<String>(', 1)
p.write_text(s, encoding='utf-8')

p = Path('lib/widgets/layers_panel.dart')
s = p.read_text(encoding='utf-8')
if "premium_catalogs.dart" not in s:
    s = s.replace("import '../state/workspace_controller.dart';", "import '../state/workspace_controller.dart';\nimport 'premium_catalogs.dart';", 1)

# advanced_layers_upgrade writes compact one-line switch cases, so support both
# compact and expanded forms and make the final layer title unambiguous.
if 'PremiumShapeCatalog.borderNames[index]' not in s:
    compact = "case ElementKind.shape: return 'Shape';"
    expanded = """      case ElementKind.shape:\n        return 'Shape';"""
    label = """case ElementKind.shape:\n        if (element.catalogType == 'border') {\n          final index = element.shapeType.clamp(0, PremiumShapeCatalog.borderNames.length - 1).toInt();\n          return 'Border • ${PremiumShapeCatalog.borderNames[index]}';\n        }\n        if (element.catalogType == 'shape') {\n          final index = element.shapeType.clamp(0, PremiumShapeCatalog.shapeNames.length - 1).toInt();\n          return 'Shape • ${PremiumShapeCatalog.shapeNames[index]}';\n        }\n        return 'Shape';"""
    if compact in s:
        s = s.replace(compact, label, 1)
    elif expanded in s:
        s = s.replace(expanded, '      ' + label, 1)
    else:
        raise SystemExit('Layers shape-title anchor not found')

compact_sub = "case ElementKind.shape:\n      case ElementKind.image: return '${element.width.round()} × ${element.height.round()}';"
if compact_sub in s:
    s = s.replace(compact_sub, "case ElementKind.shape: { final kind = element.catalogType == 'border' ? 'Border' : 'Shape'; return '$kind • ${element.width.round()} × ${element.height.round()}'; }\n      case ElementKind.image: return '${element.width.round()} × ${element.height.round()}';", 1)

s = s.replace(
    'final index = element.shapeType.clamp(0, PremiumShapeCatalog.borderNames.length - 1);',
    'final index = element.shapeType.clamp(0, PremiumShapeCatalog.borderNames.length - 1).toInt();',
)
s = s.replace(
    'final index = element.shapeType.clamp(0, PremiumShapeCatalog.shapeNames.length - 1);',
    'final index = element.shapeType.clamp(0, PremiumShapeCatalog.shapeNames.length - 1).toInt();',
)
p.write_text(s, encoding='utf-8')

ws = Path('lib/screens/workspace_screen.dart').read_text(encoding='utf-8')
layers = Path('lib/widgets/layers_panel.dart').read_text(encoding='utf-8')
checks = [
    ('Future<void> _layersSheet() async', ws),
    ("tooltip: 'Layers'", ws),
    ('_deselectTool()', ws),
    ("PremiumShapeCatalog.borderNames[index]", layers),
    ("element.catalogType == 'border'", layers),
    ('.clamp(0, PremiumShapeCatalog.borderNames.length - 1).toInt()', layers),
]
for needle, text in checks:
    if needle not in text:
        raise SystemExit(f'Final UX safety invariant missing: {needle}')
print('Final editor UX safety contracts verified.')
