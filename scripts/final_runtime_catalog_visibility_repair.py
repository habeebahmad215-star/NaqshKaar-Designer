from pathlib import Path

# Final runtime guard: catalog elements must occupy their full model bounds.
# Keep this pass focused on the catalog painter itself. The canvas interaction
# layer already owns hit-testing and sizing; wrapping the entire GestureDetector
# here can create mismatched generated closures when earlier passes have changed
# the surrounding widget tree.
p = Path('lib/widgets/design_canvas.dart')
s = p.read_text(encoding='utf-8')

old_generated = """      case ElementKind.shape:\n        if (e.catalogType == 'shape' || e.catalogType == 'border') {\n          child = CustomPaint(painter: CatalogShapePainter(type: e.shapeType, fill: e.color, stroke: e.strokeColor.a > 0 ? e.strokeColor : _purple, strokeWidth: e.strokeWidth > 0 ? e.strokeWidth : 3, border: e.catalogType == 'border'));\n        } else {\n          child = DecoratedBox(decoration: _decoration(e, isShape: true));\n        }\n        break;"""
new_generated = """      case ElementKind.shape:\n        if (e.catalogType == 'shape' || e.catalogType == 'border') {\n          final stroke = e.strokeColor.a > 0 ? e.strokeColor : _purple;\n          final strokeWidth = e.strokeWidth > 0 ? e.strokeWidth : 3;\n          final catalog = CustomPaint(\n            size: Size(e.width, e.height),\n            isComplex: true,\n            willChange: true,\n            painter: CatalogShapePainter(\n              type: e.shapeType,\n              fill: e.color,\n              stroke: stroke,\n              strokeWidth: strokeWidth,\n              border: e.catalogType == 'border',\n            ),\n          );\n          final base = e.catalogType == 'border'\n              ? DecoratedBox(\n                  decoration: BoxDecoration(\n                    border: Border.all(color: stroke, width: strokeWidth),\n                  ),\n                )\n              : const SizedBox.expand();\n          child = Stack(fit: StackFit.expand, children: [base, catalog]);\n        } else {\n          child = DecoratedBox(decoration: _decoration(e, isShape: true));\n        }\n        break;"""

if old_generated in s:
    s = s.replace(old_generated, new_generated, 1)
elif "final catalog = CustomPaint(" not in s:
    raise SystemExit('Generated catalog shape block not found')

p.write_text(s, encoding='utf-8')
print('Final runtime catalog visibility guard applied without touching GestureDetector structure.')