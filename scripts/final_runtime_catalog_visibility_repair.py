from pathlib import Path
import re

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

# Final numeric normalization for selection-handle dimensions. dart:math
# min/max return num, while Flutter widget dimensions require double. Use a
# class-local helper so the generated source contains no num-valued dimensions.
patterns = [
    (r'math\.max\(touch,\s*math\.min\(e\.width,\s*180\.0\)\)(?:\.toDouble\(\))?', '_handleSpan(e.width, touch)'),
    (r'math\.max\(touch,\s*math\.min\(e\.height,\s*180\.0\)\)(?:\.toDouble\(\))?', '_handleSpan(e.height, touch)'),
]
for pattern, replacement in patterns:
    s = re.sub(pattern, replacement, s)

# Also normalize equivalent expressions if a previous generator changes
# whitespace or adds an explicit conversion.
s = s.replace('math.max(touch, math.min(e.width, 180))', '_handleSpan(e.width, touch)')
s = s.replace('math.max(touch, math.min(e.height, 180))', '_handleSpan(e.height, touch)')

if '_handleSpan(double extent, double minimum)' not in s:
    marker = '  Widget _edgeHandle(DesignElement e, String type, Alignment alignment) {'
    helper = '''  double _handleSpan(double extent, double minimum) {\n    final bounded = extent > 180.0 ? 180.0 : extent;\n    return bounded > minimum ? bounded : minimum;\n  }\n\n'''
    if marker not in s:
        raise SystemExit('Edge handle anchor not found; refusing unsafe insertion')
    s = s.replace(marker, helper + marker, 1)

# Fail the build-stage transformation immediately if a known unsafe numeric
# expression somehow survives another generator. This is safer than letting
# flutter analyze discover it much later.
if re.search(r'math\.max\(touch,\s*math\.min\(e\.(?:width|height),\s*180\.0\)\)', s):
    raise SystemExit('Unsafe num-valued selection handle expression survived final normalization')
if '_handleSpan(e.width, touch)' not in s or '_handleSpan(e.height, touch)' not in s:
    raise SystemExit('Final selection handle double normalization was not applied')

p.write_text(s, encoding='utf-8')
print('Final runtime catalog visibility and canvas numeric type safety applied.')
