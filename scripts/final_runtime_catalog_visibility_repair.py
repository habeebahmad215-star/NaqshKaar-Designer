from pathlib import Path

# Final runtime guard: catalog elements must always occupy their full model
# bounds. This prevents CustomPaint from receiving loose/zero-size constraints
# inside the interactive editor and gives borders a guaranteed visible base
# stroke even if a decorative painter variant has a rendering edge case.
p = Path('lib/widgets/design_canvas.dart')
s = p.read_text(encoding='utf-8')

old = """      case ElementKind.shape:\n        child = DecoratedBox(decoration: _decoration(e, isShape: true));\n        break;"""
new = """      case ElementKind.shape:\n        if (e.catalogType == 'shape' || e.catalogType == 'border') {\n          final catalog = CustomPaint(\n            size: Size(e.width, e.height),\n            isComplex: true,\n            willChange: true,\n            painter: CatalogShapePainter(\n              type: e.shapeType,\n              fill: e.color,\n              stroke: e.strokeColor.a > 0 ? e.strokeColor : _purple,\n              strokeWidth: e.strokeWidth > 0 ? e.strokeWidth : 3,\n              border: e.catalogType == 'border',\n            ),\n          );\n          final base = e.catalogType == 'border'\n              ? DecoratedBox(\n                  decoration: BoxDecoration(\n                    border: Border.all(\n                      color: e.strokeColor.a > 0 ? e.strokeColor : _purple,\n                      width: e.strokeWidth > 0 ? e.strokeWidth : 3,\n                    ),\n                  ),\n                )\n              : const SizedBox.expand();\n          child = Stack(fit: StackFit.expand, children: [base, catalog]);\n        } else {\n          child = DecoratedBox(decoration: _decoration(e, isShape: true));\n        }\n        break;"""
if old in s:
    s = s.replace(old, new, 1)
elif "final catalog = CustomPaint(" not in s:
    raise SystemExit('Expected catalog shape rendering block was not found')

# Explicitly constrain the interactive child to the element model bounds.
old_wrap = """            child: GestureDetector(\n              behavior: HitTestBehavior.opaque,"""
new_wrap = """            child: SizedBox.expand(\n              child: GestureDetector(\n                behavior: HitTestBehavior.opaque,"""
if old_wrap in s and "child: SizedBox.expand(\n              child: GestureDetector(" not in s:
    s = s.replace(old_wrap, new_wrap, 1)
    old_end = """              child: child,\n            ),\n            if (selected && !e.locked) _selectionHandles(e),"""
    new_end = """                child: child,\n              ),\n            ),\n            if (selected && !e.locked) _selectionHandles(e),"""
    if old_end not in s:
        raise SystemExit('Expected gesture child closing block was not found')
    s = s.replace(old_end, new_end, 1)

p.write_text(s, encoding='utf-8')
print('Final runtime catalog visibility guard applied.')
