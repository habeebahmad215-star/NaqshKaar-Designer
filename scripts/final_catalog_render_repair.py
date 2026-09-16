from pathlib import Path

p = Path('lib/widgets/premium_catalogs.dart')
s = p.read_text(encoding='utf-8')

# Replace the complete border method using stable class-method anchors.
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
        for (final o in [Offset(q.left, q.top), Offset(q.right, q.top), Offset(q.left, q.bottom), Offset(q.right, q.bottom)]) {
          c.drawCircle(o, p.strokeWidth * 1.25, p);
        }
        break;
      case 8:
        final b = Paint()..color = p.color..style = PaintingStyle.stroke..strokeWidth = p.strokeWidth * 1.8;
        c.drawRect(q, b);
        break;
      case 9:
        final b = Paint()..color = p.color.withValues(alpha: .55)..style = PaintingStyle.stroke..strokeWidth = p.strokeWidth * 1.5;
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
      for (final o in [Offset(q.left, q.top), Offset(q.right, q.top), Offset(q.left, q.bottom), Offset(q.right, q.bottom)]) {
        c.drawCircle(o, corner, p);
      }
    }
  }

'''
s = s[:start] + method + s[end:]

# Normalize CatalogShapePainter: remove every existing shouldRepaint method
# (including block-form and expression-form declarations), then add exactly one.
cls = s.find('class CatalogShapePainter')
if cls < 0:
    raise SystemExit('CatalogShapePainter class not found')
next_cls = s.find('\nclass ', cls + 1)
cls_end = next_cls if next_cls >= 0 else len(s)
segment = s[cls:cls_end]

while True:
    pos = segment.find('shouldRepaint(')
    if pos < 0:
        break
    decl_start = segment.rfind('@override', 0, pos)
    if decl_start < 0:
        decl_start = segment.rfind('\n', 0, pos) + 1
    arrow = segment.find('=>', pos)
    brace = segment.find('{', pos)
    if arrow >= 0 and (brace < 0 or arrow < brace):
        semi = segment.find(';', arrow)
        if semi < 0:
            raise SystemExit('Could not terminate shouldRepaint expression')
        decl_end = semi + 1
    elif brace >= 0:
        depth = 0
        decl_end = None
        for i in range(brace, len(segment)):
            if segment[i] == '{':
                depth += 1
            elif segment[i] == '}':
                depth -= 1
                if depth == 0:
                    decl_end = i + 1
                    break
        if decl_end is None:
            raise SystemExit('Could not terminate shouldRepaint block')
    else:
        raise SystemExit('Could not locate shouldRepaint body')
    segment = segment[:decl_start] + segment[decl_end:]

paint_marker = '  @override void paint(Canvas canvas, Size size) {'
paint_pos = segment.find(paint_marker)
if paint_pos < 0:
    raise SystemExit('CatalogShapePainter paint method not found')
repaint = '  @override bool shouldRepaint(covariant CatalogShapePainter oldDelegate) => oldDelegate.type != type || oldDelegate.fill != fill || oldDelegate.stroke != stroke || oldDelegate.strokeWidth != strokeWidth || oldDelegate.border != border;\n'
segment = segment[:paint_pos] + repaint + segment[paint_pos:]
s = s[:cls] + segment + s[cls_end:]

p.write_text(s, encoding='utf-8')
print('Final catalog border renderer and repaint safety repaired.')
