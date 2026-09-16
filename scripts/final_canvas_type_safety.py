from pathlib import Path

# Final source-level type normalization for the mobile selection handles.
# Keep this pass deliberately narrow: it runs after every canvas/UI generator,
# so generated Dart is checked in its final form before dart fix/format/analyze.
p = Path('lib/widgets/design_canvas.dart')
s = p.read_text(encoding='utf-8')

# Dart's dart:math min/max APIs are typed as num. Avoid relying on inference in
# widget dimension expressions by using a class-local double-only helper.
s = s.replace(
    'math.max(touch, math.min(e.width, 180.0)).toDouble()',
    '_handleSpan(e.width, touch)',
)
s = s.replace(
    'math.max(touch, math.min(e.height, 180.0)).toDouble()',
    '_handleSpan(e.height, touch)',
)
s = s.replace(
    'math.max(touch, math.min(e.width, 180.0))',
    '_handleSpan(e.width, touch)',
)
s = s.replace(
    'math.max(touch, math.min(e.height, 180.0))',
    '_handleSpan(e.height, touch)',
)

if '_handleSpan(double extent, double minimum)' not in s:
    marker = '  Widget _rotationHandle(DesignElement e) {'
    helper = '''  double _handleSpan(double extent, double minimum) {
    final bounded = extent > 180.0 ? 180.0 : extent;
    return bounded > minimum ? bounded : minimum;
  }

'''
    if marker not in s:
        raise SystemExit('Rotation handle anchor not found; refusing unsafe insertion')
    s = s.replace(marker, helper + marker, 1)

p.write_text(s, encoding='utf-8')
print('Final canvas numeric type safety applied.')
