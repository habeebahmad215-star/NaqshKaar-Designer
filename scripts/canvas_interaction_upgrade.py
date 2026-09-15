from pathlib import Path
import re

controller_path = Path('lib/state/workspace_controller.dart')
text = controller_path.read_text()

if 'double? guideX;' not in text:
    text = text.replace(
        '  bool _continuousCheckpointActive = false;\n',
        '  bool _continuousCheckpointActive = false;\n\n'
        '  // Transient smart-guide coordinates; never serialized.\n'
        '  double? guideX;\n'
        '  double? guideY;\n\n'
        '  void _clearGuides() { guideX = null; guideY = null; }\n'
    )

text = text.replace(
    '  void select(String? id) { selectedId = id; notifyListeners(); }',
    '  void select(String? id) { selectedId = id; _clearGuides(); notifyListeners(); }'
)

move_pattern = r'  void moveSelectedBy\(double dx, double dy\) \{.*?\n  \}\n\n  /// Resizes'
move_replacement = r'''  void moveSelectedBy(double dx, double dy) {
    final e = selected;
    if (e == null || e.locked) return;
    var nextX = (e.x + dx).clamp(-e.width * .75, page.size.width - e.width * .25).toDouble();
    var nextY = (e.y + dy).clamp(-e.height * .75, page.size.height - e.height * .25).toDouble();
    const snap = 10.0;
    double? gx;
    double? gy;

    // Snap the element's three horizontal anchors to the page and other objects.
    final xAnchors = <({double position, double delta})>[
      (position: nextX, delta: 0),
      (position: nextX + e.width / 2, delta: e.width / 2),
      (position: nextX + e.width, delta: e.width),
    ];
    final yAnchors = <({double position, double delta})>[
      (position: nextY, delta: 0),
      (position: nextY + e.height / 2, delta: e.height / 2),
      (position: nextY + e.height, delta: e.height),
    ];
    final xTargets = <double>[0, page.size.width / 2, page.size.width];
    final yTargets = <double>[0, page.size.height / 2, page.size.height];
    for (final other in elements) {
      if (other.id == e.id || other.hidden) continue;
      xTargets.addAll([other.x, other.x + other.width / 2, other.x + other.width]);
      yTargets.addAll([other.y, other.y + other.height / 2, other.y + other.height]);
    }
    for (final anchor in xAnchors) {
      final target = xTargets.fold<double?>(null, (best, value) {
        if ((anchor.position - value).abs() > snap) return best;
        if (best == null || (anchor.position - value).abs() < (anchor.position - best).abs()) return value;
        return best;
      });
      if (target != null) {
        nextX += target - anchor.position;
        gx = target;
        break;
      }
    }
    for (final anchor in yAnchors) {
      final target = yTargets.fold<double?>(null, (best, value) {
        if ((anchor.position - value).abs() > snap) return best;
        if (best == null || (anchor.position - value).abs() < (anchor.position - best).abs()) return value;
        return best;
      });
      if (target != null) {
        nextY += target - anchor.position;
        gy = target;
        break;
      }
    }

    e.x = nextX;
    e.y = nextY;
    guideX = gx;
    guideY = gy;
    _changed();
  }

  /// Small precision movement for future keyboard/accessibility controls.
  void nudgeSelected(double dx, double dy) {
    final e = selected;
    if (e == null || e.locked) return;
    _checkpoint();
    e.x = (e.x + dx).clamp(-e.width * .75, page.size.width - e.width * .25).toDouble();
    e.y = (e.y + dy).clamp(-e.height * .75, page.size.height - e.height * .25).toDouble();
    _clearGuides();
    _changed();
  }

  /// Resizes'''
text, n = re.subn(move_pattern, move_replacement, text, count=1, flags=re.S)
if n != 1:
    raise SystemExit('moveSelectedBy block not found')

text = text.replace(
    '  void finishContinuousEdit() { _continuousCheckpointActive = false; notifyListeners(); }',
    '  void finishContinuousEdit() { _continuousCheckpointActive = false; _clearGuides(); notifyListeners(); }'
)
for old, new in [
    ('selectedId = null; _changed(); }', 'selectedId = null; _clearGuides(); _changed(); }'),
    ('selectedId = null; _changed(); }\n  void duplicatePage', 'selectedId = null; _clearGuides(); _changed(); }\n  void duplicatePage'),
]:
    text = text.replace(old, new)
controller_path.write_text(text)

canvas_path = Path('lib/widgets/design_canvas.dart')
canvas = canvas_path.read_text()
needle = "        Positioned(\n          top: 8,\n          right: 8,\n          child: Material("
if needle in canvas and 'AlignmentGuidesPainter' not in canvas:
    overlay = '''        if (controller.guideX != null || controller.guideY != null)
          Positioned.fill(
            child: IgnorePointer(
              child: CustomPaint(
                painter: _AlignmentGuidesPainter(
                  guideX: controller.guideX,
                  guideY: controller.guideY,
                  color: const Color(0xFFEF4444),
                  strokeWidth: 1.0,
                ),
              ),
            ),
          ),
'''
    canvas = canvas.replace(needle, overlay + needle, 1)
    canvas += '''\n\nclass _AlignmentGuidesPainter extends CustomPainter {
  final double? guideX;
  final double? guideY;
  final Color color;
  final double strokeWidth;
  const _AlignmentGuidesPainter({required this.guideX, required this.guideY, required this.color, required this.strokeWidth});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = color..strokeWidth = strokeWidth;
    const dash = 7.0;
    const gap = 5.0;
    void dashedLine(Offset a, Offset b) {
      final distance = (b - a).distance;
      if (distance <= 0) return;
      final direction = (b - a) / distance;
      var traveled = 0.0;
      while (traveled < distance) {
        final end = math.min(traveled + dash, distance);
        canvas.drawLine(a + direction * traveled, a + direction * end, paint);
        traveled += dash + gap;
      }
    }
    if (guideX != null) {
      dashedLine(Offset(guideX!, 0), Offset(guideX!, size.height));
    }
    if (guideY != null) {
      dashedLine(Offset(0, guideY!), Offset(size.width, guideY!));
    }
  }

  @override
  bool shouldRepaint(covariant _AlignmentGuidesPainter old) => old.guideX != guideX || old.guideY != guideY || old.color != color || old.strokeWidth != strokeWidth;
}
'''
canvas_path.write_text(canvas)
print('Canvas smart snapping, guides and precision nudge upgrade applied')
