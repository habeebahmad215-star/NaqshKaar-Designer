from pathlib import Path

ROOT = Path('.')
MODELS = ROOT / 'lib/models/design_models.dart'
CONTROLLER = ROOT / 'lib/state/workspace_controller.dart'
CANVAS = ROOT / 'lib/widgets/design_canvas.dart'
WORKSPACE = ROOT / 'lib/screens/workspace_screen.dart'


def patch_once(path, old, new, label):
    text = path.read_text(encoding='utf-8')
    if new in text:
        return
    if old not in text:
        raise SystemExit(f'Border upgrade: expected {label} was not found in {path}')
    path.write_text(text.replace(old, new, 1), encoding='utf-8')


# Model: keep borders as ordinary design elements so they naturally support move,
# resize, rotate, lock, duplicate, layers and project persistence.
patch_once(
    MODELS,
    "  double radius;\n",
    "  double radius;\n  int borderStyle;\n",
    'model field anchor',
)
patch_once(
    MODELS,
    "    this.imageBytes,\n    this.radius = 18,\n",
    "    this.imageBytes,\n    this.radius = 18,\n    this.borderStyle = 0,\n",
    'model constructor anchor',
)
patch_once(
    MODELS,
    "        'imageBytes': imageBytes == null ? null : base64Encode(imageBytes!), 'radius': radius,\n",
    "        'imageBytes': imageBytes == null ? null : base64Encode(imageBytes!), 'radius': radius, 'borderStyle': borderStyle,\n",
    'model serialization anchor',
)
patch_once(
    MODELS,
    "      imageBytes: bytes, radius: (json['radius'] as num?)?.toDouble() ?? 18,\n",
    "      imageBytes: bytes, radius: (json['radius'] as num?)?.toDouble() ?? 18, borderStyle: ((json['borderStyle'] as num?)?.toInt() ?? 0).clamp(0, 100),\n",
    'model deserialization anchor',
)

# Controller: add a ready-made border with a transparent center.
patch_once(
    CONTROLLER,
    "  DesignElement addShape() { _checkpoint(); final e = DesignElement(id: _newId('shape'), kind: ElementKind.shape, x: page.size.width * .35, y: page.size.height * .3, width: 320, height: 220, colorValue: const Color(0xFF7C3AED).toARGB32()); page.elements.add(e); selectedId = e.id; _changed(); return e; }\n",
    "  DesignElement addShape() { _checkpoint(); final e = DesignElement(id: _newId('shape'), kind: ElementKind.shape, x: page.size.width * .35, y: page.size.height * .3, width: 320, height: 220, colorValue: const Color(0xFF7C3AED).toARGB32()); page.elements.add(e); selectedId = e.id; _changed(); return e; }\n  DesignElement addBorder(int style) { _checkpoint(); final inset = math.max(28.0, page.size.width * .045); final e = DesignElement(id: _newId('border'), kind: ElementKind.shape, x: inset, y: inset, width: page.size.width - inset * 2, height: page.size.height - inset * 2, colorValue: Colors.transparent.toARGB32(), strokeColorValue: const Color(0xFFD4AF37).toARGB32(), strokeWidth: 8, radius: 22, borderStyle: style.clamp(1, 100)); page.elements.add(e); selectedId = e.id; _changed(); return e; }\n",
    'controller addShape anchor',
)

# Canvas: border elements are painted by a single performant CustomPainter. No
# bitmap assets are needed, so 100 designs stay tiny and scale to any canvas.
patch_once(
    CANVAS,
    "      case ElementKind.shape:\n        child = DecoratedBox(decoration: _decoration(e, isShape: true));\n        break;\n",
    "      case ElementKind.shape:\n        child = e.borderStyle > 0\n            ? CustomPaint(painter: _ReadyBorderPainter(style: e.borderStyle, color: e.strokeColor.a > 0 ? e.strokeColor : e.color, strokeWidth: e.strokeWidth), child: const SizedBox.expand())\n            : DecoratedBox(decoration: _decoration(e, isShape: true));\n        break;\n",
    'canvas shape renderer anchor',
)

# Add painter before the existing selection painter.
painter = r'''
class _ReadyBorderPainter extends CustomPainter {
  final int style;
  final Color color;
  final double strokeWidth;
  const _ReadyBorderPainter({required this.style, required this.color, required this.strokeWidth});

  @override
  void paint(Canvas canvas, Size size) {
    final s = style.clamp(1, 100);
    final pad = math.max(10.0, strokeWidth * 1.2);
    final rect = Rect.fromLTWH(pad, pad, math.max(1, size.width - pad * 2), math.max(1, size.height - pad * 2));
    final p = Paint()..color = color.withValues(alpha: color.a.clamp(0.2, 1))..style = PaintingStyle.stroke..strokeWidth = math.max(2, strokeWidth);
    p.strokeCap = StrokeCap.round;
    p.strokeJoin = StrokeJoin.round;

    final family = (s - 1) ~/ 10;
    final variant = (s - 1) % 10;
    final r = rect.deflate(math.min(rect.width, rect.height) * (0.02 + variant * 0.008));

    if (family == 0) {
      p.strokeWidth = strokeWidth * (0.7 + variant * .12);
      canvas.drawRRect(RRect.fromRectAndRadius(r, Radius.circular(6 + variant * 4.0)), p);
      if (variant.isEven) canvas.drawRRect(RRect.fromRectAndRadius(r.deflate(10 + variant), Radius.circular(4 + variant * 2.0)), p);
    } else if (family == 1) {
      p.strokeWidth = strokeWidth * .75;
      _drawDashed(canvas, r, p, 10 + variant * 2.0, 5 + variant);
      if (variant >= 5) _drawDashed(canvas, r.deflate(10), p, 3 + variant * .7, 5);
    } else if (family == 2) {
      p.strokeWidth = strokeWidth * .72;
      _drawDotted(canvas, r, p, 5 + variant * .8, 5 + variant * .5);
    } else if (family == 3) {
      p.strokeWidth = strokeWidth * .65;
      _drawZigZag(canvas, r, p, 8 + variant * 1.2, 5 + variant * .6);
    } else if (family == 4) {
      p.strokeWidth = strokeWidth * .68;
      _drawScallop(canvas, r, p, 10 + variant * 1.5);
      if (variant >= 4) _drawScallop(canvas, r.deflate(9), p, 6 + variant);
    } else if (family == 5) {
      p.strokeWidth = strokeWidth * .7;
      _drawDiamond(canvas, r, p, 11 + variant * 1.8);
      if (variant.isOdd) _drawDiamond(canvas, r.deflate(7), p, 7 + variant);
    } else if (family == 6) {
      p.strokeWidth = strokeWidth * .72;
      _drawFloral(canvas, r, p, 8 + variant * 1.4, variant);
    } else if (family == 7) {
      p.strokeWidth = strokeWidth * .72;
      _drawCornerOrnament(canvas, r, p, variant);
      if (variant >= 5) _drawCornerOrnament(canvas, r.deflate(7), p, variant - 5);
    } else if (family == 8) {
      p.strokeWidth = strokeWidth * .72;
      _drawArabicGeometry(canvas, r, p, 12 + variant * 2.0, variant);
    } else {
      p.strokeWidth = strokeWidth * (0.62 + variant * .06);
      _drawRoyal(canvas, r, p, variant);
    }
    if (variant == 8 || variant == 9) {
      final q = r.deflate(12 + variant);
      canvas.drawRRect(RRect.fromRectAndRadius(q, const Radius.circular(4)), p..strokeWidth = math.max(1.5, strokeWidth * .35));
    }
  }

  void _drawDashed(Canvas c, Rect r, Paint p, double dash, double gap) {
    _pathAlongRect(c, r, p, (a, b) {
      final length = (b - a).distance;
      var t = 0.0;
      while (t < length) {
        final end = math.min(length, t + dash);
        final q1 = a + (b - a) * (t / length);
        final q2 = a + (b - a) * (end / length);
        c.drawLine(q1, q2, p);
        t += dash + gap;
      }
    });
  }

  void _drawDotted(Canvas c, Rect r, Paint p, double radius, double gap) {
    final step = radius * 2 + gap;
    for (final side in [0, 1, 2, 3]) {
      final len = side.isEven ? r.width : r.height;
      for (var d = 0.0; d <= len; d += step) {
        final o = side == 0 ? Offset(r.left + d, r.top) : side == 1 ? Offset(r.right, r.top + d) : side == 2 ? Offset(r.right - d, r.bottom) : Offset(r.left, r.bottom - d);
        c.drawCircle(o, radius * .55, p..style = PaintingStyle.fill);
      }
    }
    p.style = PaintingStyle.stroke;
  }

  void _drawZigZag(Canvas c, Rect r, Paint p, double amp, double step) {
    _pathAlongRect(c, r, p, (a, b) {
      final len = (b - a).distance;
      final n = math.max(1, (len / step).round());
      final v = (b - a) / n;
      final normal = Offset(-v.dy, v.dx);
      final path = Path()..moveTo(a.dx, a.dy);
      for (var i = 1; i <= n; i++) {
        final base = a + v * i;
        final off = normal * (i.isOdd ? amp : -amp) / math.max(1, normal.distance);
        path.lineTo((base + off).dx, (base + off).dy);
      }
      c.drawPath(path, p);
    });
  }

  void _drawScallop(Canvas c, Rect r, Paint p, double radius) {
    _pathAlongRect(c, r, p, (a, b) {
      final len = (b - a).distance;
      final n = math.max(1, (len / (radius * 2)).round());
      final v = (b - a) / n;
      final normal = Offset(-v.dy, v.dx);
      final path = Path()..moveTo(a.dx, a.dy);
      for (var i = 0; i < n; i++) {
        final start = a + v * i;
        final end = a + v * (i + 1);
        final mid = (start + end) / 2 + normal * radius * .55 / math.max(1, normal.distance);
        path.quadraticBezierTo(mid.dx, mid.dy, end.dx, end.dy);
      }
      c.drawPath(path, p);
    });
  }

  void _drawDiamond(Canvas c, Rect r, Paint p, double step) {
    _pathAlongRect(c, r, p, (a, b) {
      final len = (b - a).distance;
      final n = math.max(1, (len / step).round());
      final v = (b - a) / n;
      final normal = Offset(-v.dy, v.dx) / math.max(1, v.distance) * step * .42;
      final path = Path()..moveTo(a.dx, a.dy);
      for (var i = 0; i < n; i++) {
        final s = a + v * i, e = a + v * (i + 1), m = (s + e) / 2;
        path.lineTo((m + normal).dx, (m + normal).dy);
        path.lineTo(e.dx, e.dy);
      }
      c.drawPath(path, p);
    });
  }

  void _drawFloral(Canvas c, Rect r, Paint p, double step, int variant) {
    _pathAlongRect(c, r, p, (a, b) {
      final len = (b - a).distance;
      final n = math.max(1, (len / step).round());
      final v = (b - a) / n;
      for (var i = 0; i <= n; i++) {
        final o = a + v * i;
        final radius = step * .34;
        c.drawCircle(o, radius, p);
        if ((i + variant).isEven) c.drawCircle(o, radius * .45, p);
      }
    });
  }

  void _drawCornerOrnament(Canvas c, Rect r, Paint p, int variant) {
    final len = 50.0 + variant * 9;
    for (final o in [Offset(r.left, r.top), Offset(r.right, r.top), Offset(r.right, r.bottom), Offset(r.left, r.bottom)]) {
      final sx = o.dx == r.left ? 1 : -1, sy = o.dy == r.top ? 1 : -1;
      final path = Path()..moveTo(o.dx, o.dy)..lineTo(o.dx + sx * len, o.dy)..moveTo(o.dx, o.dy)..lineTo(o.dx, o.dy + sy * len);
      c.drawPath(path, p);
      c.drawCircle(Offset(o.dx + sx * len * .72, o.dy + sy * len * .72), 4 + variant, p);
    }
    if (variant >= 3) canvas.drawRRect(RRect.fromRectAndRadius(r, Radius.circular(10 + variant)), p);
  }

  void _drawArabicGeometry(Canvas c, Rect r, Paint p, double step, int variant) {
    final path = Path();
    final count = 4 + (variant % 4);
    for (var i = 0; i <= count; i++) {
      final x = r.left + r.width * i / count;
      path.moveTo(x, r.top);
      path.lineTo(x + (i.isEven ? step : -step), r.bottom);
    }
    for (var i = 0; i <= count; i++) {
      final y = r.top + r.height * i / count;
      path.moveTo(r.left, y);
      path.lineTo(r.right, y + (i.isEven ? step : -step));
    }
    c.save();
    c.clipRect(r);
    c.drawPath(path, p);
    c.restore();
    canvas.drawRRect(RRect.fromRectAndRadius(r, Radius.circular(8 + variant)), p);
  }

  void _drawRoyal(Canvas c, Rect r, Paint p, int variant) {
    final outer = RRect.fromRectAndRadius(r, Radius.circular(variant.isEven ? 18 : 4));
    c.drawRRect(outer, p);
    final inner = r.deflate(12 + variant);
    c.drawRRect(RRect.fromRectAndRadius(inner, Radius.circular(variant.isEven ? 8 : 2)), p);
    final starR = 3.5 + variant * .6;
    final count = 8 + variant;
    for (var i = 0; i < count; i++) {
      final t = i / count;
      final top = Offset(r.left + r.width * t, r.top);
      final bottom = Offset(r.right - r.width * t, r.bottom);
      _star(c, top, p, starR);
      _star(c, bottom, p, starR);
    }
  }

  void _star(Canvas c, Offset o, Paint p, double radius) {
    final path = Path();
    for (var i = 0; i < 10; i++) {
      final a = -math.pi / 2 + i * math.pi / 5;
      final rr = i.isEven ? radius : radius * .42;
      final q = o + Offset(math.cos(a), math.sin(a)) * rr;
      if (i == 0) path.moveTo(q.dx, q.dy); else path.lineTo(q.dx, q.dy);
    }
    path.close();
    c.drawPath(path, p);
  }

  void _pathAlongRect(Canvas c, Rect r, Paint p, void Function(Offset, Offset) draw) {
    draw(Offset(r.left, r.top), Offset(r.right, r.top));
    draw(Offset(r.right, r.top), Offset(r.right, r.bottom));
    draw(Offset(r.right, r.bottom), Offset(r.left, r.bottom));
    draw(Offset(r.left, r.bottom), Offset(r.left, r.top));
  }

  @override
  bool shouldRepaint(covariant _ReadyBorderPainter old) => old.style != style || old.color != color || old.strokeWidth != strokeWidth;
}

'''
patch_once(CANVAS, 'class _SelectionBorderPainter extends CustomPainter {', painter + 'class _SelectionBorderPainter extends CustomPainter {', 'border painter insertion')

# Workspace: add a dedicated Border tool and a searchable, grouped 100-style gallery.
patch_once(
    WORKSPACE,
    "        _mainTool(Icons.image_outlined, 'Image', _pickImage),\n",
    "        _mainTool(Icons.image_outlined, 'Image', _pickImage),\n        _mainTool(Icons.border_style_rounded, 'Borders', _borderSheet),\n",
    'main toolbar anchor',
)

border_methods = r'''
  Future<void> _borderSheet() async {
    var query = '';
    await showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      showDragHandle: true,
      builder: (sheetContext) {
        return StatefulBuilder(
          builder: (context, setSheetState) {
            final q = query.trim().toLowerCase();
            final items = List<int>.generate(100, (i) => i + 1).where((i) {
              if (q.isEmpty) return true;
              final family = ((i - 1) ~/ 10) + 1;
              return 'border $i style $family ${_borderFamilyName(family)}'.contains(q);
            }).toList();
            return SafeArea(
              child: SizedBox(
                height: MediaQuery.sizeOf(context).height * .84,
                child: Column(
                  children: [
                    const _SheetHeader('100 Ready-Made Borders', 'Premium • Islamic • Geometric • Classic • Decorative'),
                    Padding(
                      padding: const EdgeInsets.fromLTRB(16, 4, 16, 10),
                      child: TextField(
                        decoration: InputDecoration(prefixIcon: const Icon(Icons.search_rounded), hintText: 'Search borders by style…', filled: true, border: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: BorderSide.none)),
                        onChanged: (v) => setSheetState(() => query = v),
                      ),
                    ),
                    Expanded(
                      child: GridView.builder(
                        padding: const EdgeInsets.fromLTRB(12, 0, 12, 20),
                        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount: 3, mainAxisSpacing: 10, crossAxisSpacing: 10, childAspectRatio: .92),
                        itemCount: items.length,
                        itemBuilder: (context, index) {
                          final style = items[index];
                          return InkWell(
                            borderRadius: BorderRadius.circular(16),
                            onTap: () { controller.addBorder(style); Navigator.pop(sheetContext); },
                            child: Container(
                              decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16), border: Border.all(color: const Color(0x14000000)), boxShadow: const [BoxShadow(blurRadius: 10, offset: Offset(0, 4), color: Color(0x0F000000))]),
                              padding: const EdgeInsets.all(8),
                              child: Column(
                                children: [
                                  Expanded(child: CustomPaint(painter: _BorderPreviewPainter(style), child: const SizedBox.expand())),
                                  const SizedBox(height: 4),
                                  Text('Border $style', style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w800)),
                                ],
                              ),
                            ),
                          );
                        },
                      ),
                    ),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }

  String _borderFamilyName(int family) => const ['Classic', 'Dashed', 'Dotted', 'Zigzag', 'Scallop', 'Diamond', 'Floral', 'Ornamental', 'Islamic Geometry', 'Royal'][family - 1];

'''
patch_once(WORKSPACE, '  Widget _viewButton(IconData icon, String tooltip, VoidCallback onTap) {', border_methods + '  Widget _viewButton(IconData icon, String tooltip, VoidCallback onTap) {', 'border sheet insertion')

preview = r'''
class _BorderPreviewPainter extends CustomPainter {
  final int style;
  const _BorderPreviewPainter(this.style);
  @override
  void paint(Canvas canvas, Size size) {
    final p = Paint()..color = const Color(0xFF6D28D9)..style = PaintingStyle.stroke..strokeWidth = 2;
    final r = Rect.fromLTWH(7, 7, size.width - 14, size.height - 14);
    final family = (style - 1) ~/ 10;
    final v = (style - 1) % 10;
    if (family == 0) {
      canvas.drawRRect(RRect.fromRectAndRadius(r, Radius.circular(4 + v * 1.5)), p);
      if (v.isEven) canvas.drawRRect(RRect.fromRectAndRadius(r.deflate(7), Radius.circular(3 + v)), p);
    } else if (family == 1) {
      _dash(canvas, r, p, 5 + v * .8, 3 + v * .3);
    } else if (family == 2) {
      for (final side in [0,1,2,3]) { final n = 7 + v; for (var i=0;i<n;i++) { final t=i/(n-1); final o=side==0?Offset(r.left+r.width*t,r.top):side==1?Offset(r.right,r.top+r.height*t):side==2?Offset(r.right-r.width*t,r.bottom):Offset(r.left,r.bottom-r.height*t); canvas.drawCircle(o, 1.8, p); } }
    } else if (family == 3) {
      _zig(canvas, r, p, 5 + v * .5);
    } else if (family == 4) {
      _scallop(canvas, r, p, 6 + v * .6);
    } else if (family == 5) {
      _diamond(canvas, r, p, 9 + v * .7);
    } else if (family == 6) {
      canvas.drawRRect(RRect.fromRectAndRadius(r, const Radius.circular(5)), p);
      for (var i=0;i<10+v;i++) { final t=i/(9+v); canvas.drawCircle(Offset(r.left+r.width*t,r.top),2,p); canvas.drawCircle(Offset(r.left+r.width*t,r.bottom),2,p); }
    } else if (family == 7) {
      canvas.drawRRect(RRect.fromRectAndRadius(r, const Radius.circular(7)), p);
      for (final o in [r.topLeft,r.topRight,r.bottomLeft,r.bottomRight]) { canvas.drawCircle(o, 5+v*.25, p); }
    } else if (family == 8) {
      canvas.drawRect(r, p);
      for (var i=0;i<4+(v%4);i++) { final x=r.left+r.width*i/(3+(v%4)); canvas.drawLine(Offset(x,r.top),Offset(x+5,r.bottom),p); }
    } else {
      canvas.drawRRect(RRect.fromRectAndRadius(r, Radius.circular(v.isEven?8:2)), p);
      canvas.drawRRect(RRect.fromRectAndRadius(r.deflate(5), Radius.circular(v.isEven?4:1)), p);
    }
  }
  void _dash(Canvas c, Rect r, Paint p, double dash, double gap) { for (final side in [0,1,2,3]) { final len=side.isEven?r.width:r.height; for (var d=0.0;d<len;d+=dash+gap) { final e=math.min(len,d+dash); final a=side==0?Offset(r.left+d,r.top):side==1?Offset(r.right,r.top+d):side==2?Offset(r.right-d,r.bottom):Offset(r.left,r.bottom-d); final b=side==0?Offset(r.left+e,r.top):side==1?Offset(r.right,r.top+e):side==2?Offset(r.right-e,r.bottom):Offset(r.left,r.bottom-e); c.drawLine(a,b,p); } } }
  void _zig(Canvas c, Rect r, Paint p, double step) { for (final side in [0,1,2,3]) { final len=side.isEven?r.width:r.height; final n=math.max(1,(len/step).round()); final v=(side.isEven?r.width:r.height)/n; final path=Path(); for(var i=0;i<=n;i++){final d=v*i; final o=side==0?Offset(r.left+d,r.top):side==1?Offset(r.right,r.top+d):side==2?Offset(r.right-d,r.bottom):Offset(r.left,r.bottom-d); if(i==0)path.moveTo(o.dx,o.dy);else path.lineTo(o.dx,o.dy);} c.drawPath(path,p);} }
  void _scallop(Canvas c, Rect r, Paint p, double radius) { canvas.drawRRect(RRect.fromRectAndRadius(r, Radius.circular(radius)), p); }
  void _diamond(Canvas c, Rect r, Paint p, double step) { canvas.drawRRect(RRect.fromRectAndRadius(r, Radius.circular(4)), p); for(var x=r.left;x<=r.right;x+=step){c.drawLine(Offset(x,r.top),Offset(math.min(r.right,x+step),r.bottom),p);} }
  @override
  bool shouldRepaint(covariant _BorderPreviewPainter old) => old.style != style;
}
'''
patch_once(CANVAS, 'class _SelectionBorderPainter extends CustomPainter {', preview + '\nclass _SelectionBorderPainter extends CustomPainter {', 'preview painter insertion')

print('Border Studio patch applied successfully')
