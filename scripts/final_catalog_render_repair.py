from pathlib import Path

p = Path('lib/widgets/premium_catalogs.dart')
s = p.read_text(encoding='utf-8')
start = s.find('  void _drawBorder(')
end = s.find('  void _dashed(', start)
if start < 0 or end < 0:
    raise SystemExit('Catalog border method anchors not found')

method = '''  void _drawBorder(Canvas c, Rect r, Paint p, int t) {
    final q = r.deflate(math.min(r.width, r.height) * .035);
    switch (t % 12) {
      case 0:
        c.drawRect(q, p);
        break;
      case 1:
        c.drawRect(q, p);
        c.drawRect(q.deflate(7), p);
        break;
      case 2:
        c.drawRect(q, p);
        c.drawRect(q.deflate(7), p);
        c.drawRect(q.deflate(14), p);
        break;
      case 3:
        c.drawRRect(RRect.fromRectAndRadius(q, const Radius.circular(24)), p);
        break;
      case 4:
        c.drawRRect(RRect.fromRectAndRadius(q, const Radius.circular(24)), p);
        c.drawRRect(RRect.fromRectAndRadius(q.deflate(8), const Radius.circular(18)), p);
        break;
      case 5:
        _dashed(c, q, p, 14, 8);
        break;
      case 6:
        _dotted(c, q, p, 8);
        break;
      case 7:
        _dashed(c, q, p, 12, 5);
        for (final o in [
          Offset(q.left, q.top),
          Offset(q.right, q.top),
          Offset(q.left, q.bottom),
          Offset(q.right, q.bottom),
        ]) {
          c.drawCircle(o, p.strokeWidth * 1.25, p);
        }
        break;
      case 8:
        final b = Paint()
          ..color = p.color
          ..style = PaintingStyle.stroke
          ..strokeWidth = p.strokeWidth * 1.8;
        c.drawRect(q, b);
        break;
      case 9:
        final b = Paint()
          ..color = p.color.withValues(alpha: .55)
          ..style = PaintingStyle.stroke
          ..strokeWidth = p.strokeWidth * 1.5;
        c.drawRRect(RRect.fromRectAndRadius(q, const Radius.circular(20)), b);
        break;
      case 10:
        c.drawRect(q.deflate(10), p);
        break;
      default:
        c.drawRect(q.inflate(5), p);
        break;
    }
    if (t >= 12) {
      final corner = math.min(q.width, q.height) * .045;
      for (final o in [
        Offset(q.left, q.top),
        Offset(q.right, q.top),
        Offset(q.left, q.bottom),
        Offset(q.right, q.bottom),
      ]) {
        c.drawCircle(o, corner, p);
      }
    }
  }

'''
s = s[:start] + method + s[end:]

# Keep exactly one repaint implementation even if an earlier catalog pass already added it.
lines = s.splitlines(keepends=True)
seen = False
out = []
for line in lines:
    if 'bool shouldRepaint(covariant CatalogShapePainter oldDelegate)' in line:
        if seen:
            continue
        seen = True
    out.append(line)
s = ''.join(out)
if not seen:
    marker = '  @override void paint(Canvas canvas, Size size) {'
    idx = s.find(marker)
    if idx < 0:
        raise SystemExit('CatalogShapePainter paint method not found')
    repaint = '  @override bool shouldRepaint(covariant CatalogShapePainter oldDelegate) => oldDelegate.type != type || oldDelegate.fill != fill || oldDelegate.stroke != stroke || oldDelegate.strokeWidth != strokeWidth || oldDelegate.border != border;\n'
    s = s[:idx] + repaint + s[idx:]

p.write_text(s, encoding='utf-8')
print('Final catalog border renderer and repaint safety repaired.')
