from pathlib import Path

# Premium library tabs must scroll on narrow phones instead of clipping.
p = Path('lib/widgets/premium_catalog_sheet.dart')
s = p.read_text(encoding='utf-8')
old = """            TabBar(
              controller: _tabs,
              tabs: const [
                Tab(text: 'Shapes 100+'),
                Tab(text: 'Borders 100+'),
                Tab(text: 'Special Text 100+'),
              ],
            ),"""
new = """            TabBar(
              controller: _tabs,
              isScrollable: true,
              tabAlignment: TabAlignment.start,
              labelPadding: const EdgeInsets.symmetric(horizontal: 14),
              tabs: const [
                Tab(text: 'Shapes • 100+'),
                Tab(text: 'Borders • 100+'),
                Tab(text: 'Special Text • 100+'),
              ],
            ),"""
if old in s:
    s = s.replace(old, new, 1)
p.write_text(s, encoding='utf-8')

# Real font-size behavior: remove automatic FittedBox shrinking.
p = Path('lib/widgets/design_canvas.dart')
s = p.read_text(encoding='utf-8')
old = """          child: FittedBox(
            fit: BoxFit.scaleDown,
            alignment: Alignment.center,
            child: SizedBox(
              width: e.width,
              child: Text("""
new = """          child: SizedBox(
            width: e.width,
            height: e.height,
            child: Text("""
if old in s:
    s = s.replace(old, new, 1)
p.write_text(s, encoding='utf-8')

# Make the later catalog shape entries visually varied instead of generic
# polygons. All 100 catalog entries remain selectable and canvas-backed.
p = Path('lib/widgets/premium_catalogs.dart')
s = p.read_text(encoding='utf-8')
old = "      default: _poly(canvas,c,_min(w,h)*.46,3+(type%7),(type%2==0?-math.pi/2:math.pi/4),p);"
new = "      default: _catalogVariant(canvas,r,c,w,h,type,p);"
if old in s and '_catalogVariant(Canvas c' not in s:
    s = s.replace(old, new, 1)
    anchor = '  double _min(double a,double b)=>a<b?a:b;'
    method = '''  void _catalogVariant(Canvas c,Rect r,Offset o,double w,double h,int type,Paint p){
    final k=type%12;
    switch(k){
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
  void _gear(Canvas c,Offset o,double outer,double inner,int teeth,Paint p){
    final path=Path();
    for(var i=0;i<teeth*2;i++){
      final a=-math.pi/2+math.pi*i/teeth;
      final rr=i.isEven?outer:inner;
      final q=o+Offset(math.cos(a)*rr,math.sin(a)*rr);
      if(i==0)path.moveTo(q.dx,q.dy);else path.lineTo(q.dx,q.dy);
    }
    path.close();c.drawPath(path,p);
  }
  void _target(Canvas c,Offset o,double radius,Paint p){
    for(var i=0;i<4;i++) c.drawCircle(o,radius*(1-i*.23),p);
  }
'''
    if anchor in s:
        s = s.replace(anchor, method + anchor, 1)
p.write_text(s, encoding='utf-8')

# Home screen screenshot polish: keep hero artwork from crowding the title and
# give the four-column feature grid a little more vertical breathing room.
p = Path('lib/screens/home_screen.dart')
s = p.read_text(encoding='utf-8')
s = s.replace('padding: const EdgeInsets.fromLTRB(20, 18, 118, 16),', 'padding: const EdgeInsets.fromLTRB(20, 18, 150, 16),', 1)
s = s.replace('fontSize: 25,\n                      fontWeight: FontWeight.w900,', 'fontSize: 22,\n                      fontWeight: FontWeight.w900,', 1)
s = s.replace('childAspectRatio: .78,', 'childAspectRatio: .72,', 1)
p.write_text(s, encoding='utf-8')

print('Deep screenshot-driven polish applied.')
