from pathlib import Path

p = Path('lib/widgets/layers_panel.dart')
s = p.read_text(encoding='utf-8')
if "import 'premium_catalogs.dart';" not in s:
    s = s.replace("import '../state/workspace_controller.dart';", "import '../state/workspace_controller.dart';\nimport 'premium_catalogs.dart';", 1)

if 'PremiumShapeCatalog.borderNames[index]' not in s:
    compact = "case ElementKind.shape: return 'Shape';"
    if compact in s:
        label = """case ElementKind.shape: {\n        if (element.catalogType == 'border') {\n          final index = element.shapeType.clamp(0, PremiumShapeCatalog.borderNames.length - 1).toInt();\n          return 'Border • ${PremiumShapeCatalog.borderNames[index]}';\n        }\n        if (element.catalogType == 'shape') {\n          final index = element.shapeType.clamp(0, PremiumShapeCatalog.shapeNames.length - 1).toInt();\n          return 'Shape • ${PremiumShapeCatalog.shapeNames[index]}';\n        }\n        return 'Shape';\n      }"""
        s = s.replace(compact, label, 1)
    else:
        raise SystemExit('Compact layer shape-title anchor not found')

s = s.replace(
    "case ElementKind.shape:\n      case ElementKind.image: return '${element.width.round()} × ${element.height.round()}';",
    "case ElementKind.shape: { final kind = element.catalogType == 'border' ? 'Border' : 'Shape'; return '$kind • ${element.width.round()} × ${element.height.round()}'; }\n      case ElementKind.image: return '${element.width.round()} × ${element.height.round()}';",
    1,
)
p.write_text(s, encoding='utf-8')
print('Layer catalog labels normalized before final editor UX pass.')
