from pathlib import Path
import re


def patch(path: str, fn):
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    updated = fn(text)
    if updated == text:
        print(f'[skip] {path}')
    else:
        p.write_text(updated, encoding='utf-8')
        print(f'[patched] {path}')


# 1) Home: use adaptive tile sizing instead of a fixed four-column phone grid.
def home_patch(s: str) -> str:
    s = s.replace(
        """const SliverGridDelegateWithFixedCrossAxisCount(\n                    crossAxisCount: 4,\n                    mainAxisSpacing: 12,\n                    crossAxisSpacing: 10,\n                    childAspectRatio: .72,\n                  )""",
        """const SliverGridDelegateWithMaxCrossAxisExtent(\n                    maxCrossAxisExtent: 176,\n                    mainAxisSpacing: 12,\n                    crossAxisSpacing: 10,\n                    childAspectRatio: .96,\n                  )""",
        1,
    )
    s = s.replace("const SliverToBoxAdapter(child: SizedBox(height: 88)),", "const SliverToBoxAdapter(child: SizedBox(height: 132)),", 1)
    s = s.replace("height: 190,", "height: 210,", 1)
    s = s.replace("padding: const EdgeInsets.fromLTRB(20, 18, 150, 16),", "padding: const EdgeInsets.fromLTRB(20, 16, 132, 14),", 1)
    s = s.replace(
        """                    maxLines: 1,\n                    overflow: TextOverflow.ellipsis,\n                    style: TextStyle(\n                      fontSize: 22,""",
        """                    maxLines: 2,\n                    softWrap: true,\n                    overflow: TextOverflow.clip,\n                    style: TextStyle(\n                      fontSize: 20,""",
        1,
    )
    s = s.replace(
        """                    maxLines: 1,\n                    overflow: TextOverflow.ellipsis,\n                    style: TextStyle(\n                      fontFamily: 'JameelNooriNastaleeq',\n                      fontSize: 20,""",
        """                    maxLines: 2,\n                    softWrap: true,\n                    overflow: TextOverflow.clip,\n                    style: TextStyle(\n                      fontFamily: 'JameelNooriNastaleeq',\n                      fontSize: 18,""",
        1,
    )
    s = s.replace(
        """                    maxLines: 1,\n                    overflow: TextOverflow.ellipsis,\n                    style: TextStyle(\n                      fontSize: 10.5,""",
        """                    maxLines: 2,\n                    softWrap: true,\n                    overflow: TextOverflow.clip,\n                    style: TextStyle(\n                      fontSize: 9.5,""",
        1,
    )
    s = s.replace("""              padding: const EdgeInsets.fromLTRB(4, 9, 4, 6),""", """              padding: const EdgeInsets.fromLTRB(7, 10, 7, 8),""", 1)
    s = s.replace(
        """                    maxLines: 1,\n                    overflow: TextOverflow.ellipsis,\n                    textAlign: TextAlign.center,\n                    style: const TextStyle(\n                      fontSize: 10.5,""",
        """                    maxLines: 2,\n                    softWrap: true,\n                    overflow: TextOverflow.clip,\n                    textAlign: TextAlign.center,\n                    style: const TextStyle(\n                      fontSize: 11,""",
        1,
    )
    s = s.replace(
        """                    maxLines: 1,\n                    overflow: TextOverflow.ellipsis,\n                    textAlign: TextAlign.center,\n                    style: const TextStyle(fontSize: 7.5, color: _muted),""",
        """                    maxLines: 2,\n                    softWrap: true,\n                    overflow: TextOverflow.clip,\n                    textAlign: TextAlign.center,\n                    style: const TextStyle(fontSize: 8.2, color: _muted),""",
        1,
    )
    return s


patch('lib/screens/home_screen.dart', home_patch)


# 2) Premium library tabs: horizontal scrolling is intentional on narrow phones.
def tabs_patch(s: str) -> str:
    old = """            TabBar(\n              controller: _tabs,\n              tabs: const [\n                Tab(text: 'Shapes 100+'),\n                Tab(text: 'Borders 100+'),\n                Tab(text: 'Special Text 100+'),\n              ],\n            ),"""
    new = """            TabBar(\n              controller: _tabs,\n              isScrollable: true,\n              tabAlignment: TabAlignment.start,\n              labelPadding: const EdgeInsets.symmetric(horizontal: 14),\n              tabs: const [\n                Tab(text: 'Shapes • 100+'),\n                Tab(text: 'Borders • 100+'),\n                Tab(text: 'Special Text • 100+'),\n              ],\n            ),"""
    if old in s:
        return s.replace(old, new, 1)
    if 'isScrollable: true' in s:
        return s
    raise SystemExit('PremiumCatalogSheet TabBar pattern not found')


patch('lib/widgets/premium_catalog_sheet.dart', tabs_patch)


# 3) Text rendering: never silently scale a user's requested font size down.
def canvas_patch(s: str) -> str:
    old = """          child: FittedBox(\n            fit: BoxFit.scaleDown,\n            alignment: Alignment.center,\n            child: SizedBox(\n              width: e.width,\n              child: Text("""
    new = """          child: SizedBox(\n            width: e.width,\n            height: e.height,\n            child: Text("""
    if old in s:
        s = s.replace(old, new, 1)
    # Generated catalog pass can reintroduce the old block; catch it by regex too.
    s = re.sub(
        r"\s*child: FittedBox\(\s*fit: BoxFit\.scaleDown,\s*alignment: Alignment\.center,\s*child: SizedBox\(\s*width: e\.width,\s*child: Text\(",
        "\n          child: SizedBox(\n            width: e.width,\n            height: e.height,\n            child: Text(",
        s,
        count=1,
    )
    return s


patch('lib/widgets/design_canvas.dart', canvas_patch)


# 4) Catalog labels must distinguish a border from an ordinary shape.
def workspace_label_patch(s: str) -> str:
    old = """  String _elementLabel(DesignElement element) {\n    switch (element.kind) {\n      case ElementKind.text:"""
    new = """  String _elementLabel(DesignElement element) {\n    if (element.catalogType == 'border') {\n      return 'Border • ${element.width.round()} × ${element.height.round()}';\n    }\n    if (element.catalogType == 'shape') {\n      return 'Shape • ${element.width.round()} × ${element.height.round()}';\n    }\n    switch (element.kind) {\n      case ElementKind.text:"""
    return s.replace(old, new, 1)


patch('lib/screens/workspace_screen.dart', workspace_label_patch)


# 5) Font-size control is exactly 5–100 px, with the current value kept readable.
def font_range_patch(s: str) -> str:
    s = s.replace("_singleSlider('Font Size', element.fontSize, 8, 300", "_singleSlider('Font Size', element.fontSize, 5, 100", 1)
    s = s.replace("e.fontSize.clamp(8, 300)", "e.fontSize.clamp(5, 100)", 1)
    s = s.replace("e.fontSize = value.clamp(5, 300)", "e.fontSize = value.clamp(5, 100)", 1)
    return s


patch('lib/screens/workspace_screen.dart', font_range_patch)
patch('lib/state/workspace_controller.dart', font_range_patch)


# 6) Make the catalog painter repaint whenever its visual parameters change.
def painter_patch(s: str) -> str:
    if 'bool shouldRepaint(covariant CatalogShapePainter oldDelegate)' in s:
        return s
    marker = "  @override void paint(Canvas canvas, Size size) {"
    idx = s.find(marker)
    if idx < 0:
        raise SystemExit('CatalogShapePainter paint method not found')
    # Insert the method immediately before paint so it is unambiguous and survives
    # the compact generated style used by the catalog source.
    method = "  @override bool shouldRepaint(covariant CatalogShapePainter oldDelegate) => oldDelegate.type != type || oldDelegate.fill != fill || oldDelegate.stroke != stroke || oldDelegate.strokeWidth != strokeWidth || oldDelegate.border != border;\n"
    return s[:idx] + method + s[idx:]


patch('lib/widgets/premium_catalogs.dart', painter_patch)


# 7) Give border families real visual identities rather than one repeating generic frame.
def border_patch(s: str) -> str:
    pattern = r"  void _drawBorder\(Canvas c,Rect r,Paint p,int t\)\{.*?\}"
    replacement = '''  void _drawBorder(Canvas c,Rect r,Paint p,int t){
    final q=r.deflate(math.min(r.width,r.height)*.035);
    switch(t%12){
      case 0: c.drawRect(q,p); break;
      case 1: c.drawRect(q,p); c.drawRect(q.deflate(7),p); break;
      case 2: c.drawRect(q,p); c.drawRect(q.deflate(7),p); c.drawRect(q.deflate(14),p); break;
      case 3: c.drawRRect(RRect.fromRectAndRadius(q,Radius.circular(24)),p); break;
      case 4: c.drawRRect(RRect.fromRectAndRadius(q,Radius.circular(24)),p); c.drawRRect(RRect.fromRectAndRadius(q.deflate(8),Radius.circular(18)),p); break;
      case 5: _dashed(c,q,p,14,8); break;
      case 6: _dotted(c,q,p,8); break;
      case 7: _dashDot(c,q,p); break;
      case 8: final b=Paint()..color=p.color..style=PaintingStyle.stroke..strokeWidth=p.strokeWidth*1.8; c.drawRect(q,b); break;
      case 9: final b=Paint()..color=p.color.withValues(alpha:.55)..style=PaintingStyle.stroke..strokeWidth=p.strokeWidth*1.5; c.drawRRect(RRect.fromRectAndRadius(q,Radius.circular(20)),b); break;
      case 10: c.drawRect(q.deflate(10),p); break;
      default: c.drawRect(q.inflate(5),p); break;
    }
    if(t>=12){
      final size=math.min(q.width,q.height)*.045;
      for(final o in [Offset(q.left,q.top),Offset(q.right,q.top),Offset(q.left,q.bottom),Offset(q.right,q.bottom)]){
        c.drawCircle(o,size,p);
      }
    }
  }
  void _dashDot(Canvas c,Rect r,Paint p){
    _dashed(c,r,p,12,5);
    for(final o in [Offset(r.left,r.top),Offset(r.right,r.top),Offset(r.left,r.bottom),Offset(r.right,r.bottom)]) c.drawCircle(o,p.strokeWidth*1.25,p);
  }'''
    return re.sub(pattern, replacement, s, count=1, flags=re.S)


patch('lib/widgets/premium_catalogs.dart', border_patch)


# 8) Keep the generated catalog shape library deterministic and distinct.
def catalog_variant_patch(s: str) -> str:
    if '_catalogVariant(Canvas c' in s:
        return s
    old = "      default: _poly(canvas,c,_min(w,h)*.46,3+(type%7),(type%2==0?-math.pi/2:math.pi/4),p);"
    new = "      default: _catalogVariant(canvas,r,c,w,h,type,p);"
    if old not in s:
        return s
    s = s.replace(old, new, 1)
    anchor = '  double _min(double a,double b)=>a<b?a:b;'
    method = '''  void _catalogVariant(Canvas c,Rect r,Offset o,double w,double h,int type,Paint p){
    switch(type%12){
      case 0: c.drawOval(r.deflate(w*.08),p); break;
      case 1: _star(c,o,_min(w,h)*.46,7,p); break;
      case 2: _star(c,o,_min(w,h)*.46,9,p); break;
      case 3: _poly(c,o,_min(w,h)*.46,10,math.pi/10,p); break;
      case 4: _poly(c,o,_min(w,h)*.46,12,math.pi/12,p); break;
      case 5: _gear(c,o,_min(w,h)*.34,_min(w,h)*.12,12,p); break;
      case 6: _target(c,o,_min(w,h)*.42,p); break;
      case 7: _ribbon(c,r,p); break;
      case 8: _shield(c,r,p); break;
      case 9: _gem(c,r,p); break;
      case 10: _flower(c,o,8,_min(w,h)*.22,p); break;
      default: _badge(c,r,p,10); break;
    }
  }
  void _gear(Canvas c,Offset o,double outer,double inner,int teeth,Paint p){final path=Path();for(var i=0;i<teeth*2;i++){final a=-math.pi/2+math.pi*i/teeth;final rr=i.isEven?outer:inner;final q=o+Offset(math.cos(a)*rr,math.sin(a)*rr);if(i==0)path.moveTo(q.dx,q.dy);else path.lineTo(q.dx,q.dy);}path.close();c.drawPath(path,p);}
  void _target(Canvas c,Offset o,double radius,Paint p){for(var i=0;i<4;i++)c.drawCircle(o,radius*(1-i*.23),p);}
'''
    if anchor in s:
        s=s.replace(anchor,method+anchor,1)
    return s


patch('lib/widgets/premium_catalogs.dart', catalog_variant_patch)

print('Deep functional repair completed: responsive home, premium tabs, exact typography, catalog labels, repaint safety and differentiated borders/shapes.')
