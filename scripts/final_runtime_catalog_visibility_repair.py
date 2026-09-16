from pathlib import Path
import re

# Final runtime guard: catalog elements must occupy their full model bounds.
# Keep this pass deterministic. Earlier generators may rewrite parts of the
# canvas, so the final pass owns the complete selection-edge implementation.
p = Path('lib/widgets/design_canvas.dart')
s = p.read_text(encoding='utf-8')

old_generated = """      case ElementKind.shape:
        if (e.catalogType == 'shape' || e.catalogType == 'border') {
          child = CustomPaint(painter: CatalogShapePainter(type: e.shapeType, fill: e.color, stroke: e.strokeColor.a > 0 ? e.strokeColor : _purple, strokeWidth: e.strokeWidth > 0 ? e.strokeWidth : 3, border: e.catalogType == 'border'));
        } else {
          child = DecoratedBox(decoration: _decoration(e, isShape: true));
        }
        break;"""
new_generated = """      case ElementKind.shape:
        if (e.catalogType == 'shape' || e.catalogType == 'border') {
          final stroke = e.strokeColor.a > 0 ? e.strokeColor : _purple;
          final double strokeWidth = e.strokeWidth > 0 ? e.strokeWidth : 3.0;
          final catalog = CustomPaint(
            size: Size(e.width, e.height),
            isComplex: true,
            willChange: true,
            painter: CatalogShapePainter(
              type: e.shapeType,
              fill: e.color,
              stroke: stroke,
              strokeWidth: strokeWidth,
              border: e.catalogType == 'border',
              radius: e.radius,
            ),
          );
          final base = e.catalogType == 'border'
              ? DecoratedBox(
                  decoration: BoxDecoration(
                    border: Border.all(color: stroke, width: strokeWidth),
                  ),
                )
              : const SizedBox.expand();
          child = Stack(fit: StackFit.expand, children: [base, catalog]);
        } else {
          child = DecoratedBox(decoration: _decoration(e, isShape: true));
        }
        break;"""
if old_generated in s:
    s = s.replace(old_generated, new_generated, 1)
elif 'radius: e.radius' not in s:
    raise SystemExit('Generated catalog shape block not found')

edge_pattern = re.compile(
    r'  Widget _edgeHandle\(DesignElement e, String type, Alignment alignment\) \{.*?\n  \}\n\n  Widget _rotationHandle\(',
    re.DOTALL,
)
edge_replacement = '''  double _handleSpan(double extent, double minimum) {
    final double bounded = extent > 180.0 ? 180.0 : extent;
    return bounded > minimum ? bounded : minimum;
  }

  Widget _edgeHandle(DesignElement e, String type, Alignment alignment) {
    final double touch = _touch / scale;
    final double visual = _edgeVisual / scale;
    final bool horizontal = alignment == Alignment.topCenter || alignment == Alignment.bottomCenter;
    final double horizontalSpan = _handleSpan(e.width, touch);
    final double verticalSpan = _handleSpan(e.height, touch);
    return Align(
      alignment: alignment,
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onPanStart: (_) { controller.select(e.id); controller.startContinuousEdit(); },
        onPanUpdate: (d) => controller.resizeSelectedFromHandle(type, d.delta.dx / scale, d.delta.dy / scale),
        onPanEnd: (_) => controller.finishContinuousEdit(),
        child: SizedBox(
          width: horizontal ? horizontalSpan : touch,
          height: horizontal ? touch : verticalSpan,
          child: Center(
            child: Container(
              width: horizontal ? 30.0 / scale : visual,
              height: horizontal ? visual : 30.0 / scale,
              decoration: BoxDecoration(
                color: _handleWhite,
                border: Border.all(color: _purple, width: 1.8 / scale),
                borderRadius: BorderRadius.circular(4.0 / scale),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _rotationHandle('''
s, count = edge_pattern.subn(edge_replacement, s, count=1)
if count != 1:
    raise SystemExit(f'Expected exactly one edge-handle function, replaced {count}')

if re.search(r'math\.max\(touch\s*,\s*math\.min\(e\.(?:width|height)', s):
    raise SystemExit('Unsafe math.max/math.min selection-handle expression survived final normalization')
if '_handleSpan(e.width, touch)' not in s or '_handleSpan(e.height, touch)' not in s:
    raise SystemExit('Final selection-handle double normalization is missing')
if 'radius: e.radius' not in s:
    raise SystemExit('Catalog radius was not wired into the painter')

p.write_text(s, encoding='utf-8')
print('Final runtime catalog visibility, radius wiring, and deterministic canvas numeric type safety applied.')