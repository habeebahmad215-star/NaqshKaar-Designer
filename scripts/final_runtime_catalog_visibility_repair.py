from pathlib import Path

# Final runtime guard: catalog elements must occupy their full model bounds.
# The catalog upgrade runs earlier in CI, so this pass targets the generated
# catalog-rendering block and makes its constraints explicit. Borders also get
# a guaranteed base stroke so a decorative painter edge case cannot make the
# selected element appear empty.
p = Path('lib/widgets/design_canvas.dart')
s = p.read_text(encoding='utf-8')

old_generated = """      case ElementKind.shape:\n        if (e.catalogType == 'shape' || e.catalogType == 'border') {\n          child = CustomPaint(painter: CatalogShapePainter(type: e.shapeType, fill: e.color, stroke: e.strokeColor.a > 0 ? e.strokeColor : _purple, strokeWidth: e.strokeWidth > 0 ? e.strokeWidth : 3, border: e.catalogType == 'border'));\n        } else {\n          child = DecoratedBox(decoration: _decoration(e, isShape: true));\n        }\n        break;"""
new_generated = """      case ElementKind.shape:\n        if (e.catalogType == 'shape' || e.catalogType == 'border') {\n          final stroke = e.strokeColor.a > 0 ? e.strokeColor : _purple;\n          final strokeWidth = e.strokeWidth > 0 ? e.strokeWidth : 3;\n          final catalog = CustomPaint(\n            size: Size(e.width, e.height),\n            isComplex: true,\n            willChange: true,\n            painter: CatalogShapePainter(\n              type: e.shapeType,\n              fill: e.color,\n              stroke: stroke,\n              strokeWidth: strokeWidth,\n              border: e.catalogType == 'border',\n            ),\n          );\n          final base = e.catalogType == 'border'\n              ? DecoratedBox(\n                  decoration: BoxDecoration(\n                    border: Border.all(color: stroke, width: strokeWidth),\n                  ),\n                )\n              : const SizedBox.expand();\n          child = Stack(fit: StackFit.expand, children: [base, catalog]);\n        } else {\n          child = DecoratedBox(decoration: _decoration(e, isShape: true));\n        }\n        break;"""

if old_generated in s:
    s = s.replace(old_generated, new_generated, 1)
elif "final catalog = CustomPaint(" not in s:
    raise SystemExit('Generated catalog shape block not found')

# Ensure every interactive element child is tightly constrained to its Positioned
# width/height, including catalog painters.
old_wrap = """            child: GestureDetector(\n              behavior: HitTestBehavior.opaque,"""
new_wrap = """            child: SizedBox.expand(\n              child: GestureDetector(\n                behavior: HitTestBehavior.opaque,"""
if old_wrap in s and "child: SizedBox.expand(\n              child: GestureDetector(" not in s:
    s = s.replace(old_wrap, new_wrap, 1)
    old_end = """              child: child,\n            ),\n            if (selected && !e.locked) _selectionHandles(e),"""
    new_end = """                child: child,\n              ),\n            ),\n            if (selected && !e.locked) _selectionHandles(e),"""
    if old_end not in s:
        raise SystemExit('Interactive child closing block not found')
    s = s.replace(old_end, new_end, 1)

p.write_text(s, encoding='utf-8')
print('Final runtime catalog visibility guard applied.')
