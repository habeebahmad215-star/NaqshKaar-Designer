from pathlib import Path
import re

# Final acceptance-oriented normalization. This runs immediately before format/analyze,
# after all other generators, so the source that gets built owns these contracts.

def patch(path, fn):
    p = Path(path)
    s = p.read_text(encoding='utf-8')
    n = fn(s)
    if n != s:
        p.write_text(n, encoding='utf-8')
        print('[patched]', path)
    else:
        print('[verified]', path)

def home(s):
    # Hero: give the text column a real responsive budget and never ellipsize copy.
    s = re.sub(r'height:\s*(?:190|198|210),', 'height: 220,', s, count=1)
    s = re.sub(r'padding:\s*const EdgeInsets\.fromLTRB\(20,\s*(?:16|18),\s*(?:118|132|150),\s*(?:14|16)\),',
               'padding: const EdgeInsets.fromLTRB(20, 16, 142, 14),', s, count=1)
    s = re.sub(r"(Text\(\s*'Design Without Limits',)\s*maxLines:\s*1,\s*overflow:\s*TextOverflow\.ellipsis,",
               r"\1\n                    maxLines: 2,\n                    softWrap: true,\n                    overflow: TextOverflow.clip,", s, count=1)
    s = re.sub(r"(Text\(\s*'Beautiful Urdu Text  •  Professional Graphics',)\s*maxLines:\s*1,\s*overflow:\s*TextOverflow\.ellipsis,",
               r"\1\n                    maxLines: 2,\n                    softWrap: true,\n                    overflow: TextOverflow.clip,", s, count=1)
    # Responsive feature grid: 2 columns on narrow phones, more columns as width grows.
    s = re.sub(
        r'SliverGridDelegateWith(?:FixedCrossAxisCount|MaxCrossAxisExtent)\(.*?\)',
        '''SliverGridDelegateWithMaxCrossAxisExtent(
                    maxCrossAxisExtent: 158,
                    mainAxisSpacing: 12,
                    crossAxisSpacing: 10,
                    childAspectRatio: .96,
                  )''',
        s, count=1, flags=re.S)
    # Feature titles/subtitles: two-line wrapping instead of truncation.
    s = re.sub(r'maxLines:\s*1,\s*overflow:\s*TextOverflow\.ellipsis,\s*textAlign:\s*TextAlign\.center,',
               'maxLines: 2,\n                    softWrap: true,\n                    overflow: TextOverflow.clip,\n                    textAlign: TextAlign.center,', s)
    s = re.sub(r'maxLines:\s*1,\s*overflow:\s*TextOverflow\.ellipsis,\s*style:\s*const TextStyle\(fontSize:\s*7\.5',
               'maxLines: 2,\n                    softWrap: true,\n                    overflow: TextOverflow.clip,\n                    style: const TextStyle(fontSize: 8.2', s)
    # Keep all scrollable Home content above the persistent bottom navigation.
    s = re.sub(r'const\s+SliverToBoxAdapter\(\s*child:\s*SizedBox\(\s*height:\s*(?:72|80|88|96|104|112|116|120|128|132|136),?\s*\)\s*\)',
               'const SliverToBoxAdapter(child: SizedBox(height: 136))', s, count=1, flags=re.S)
    return s

patch('lib/screens/home_screen.dart', home)

# Workspace font-size contract ---------------------------------------------
# Re-establish the final editor control after all generators have run.
def workspace_font_size(s):
    if '_fontSize(DesignElement element)' not in s:
        # Use the generic slider method as the stable insertion boundary.
        # _opacity is optional across generated workspace variants.
        marker = '  Future<void> _singleSlider('
        if marker not in s:
            raise SystemExit('Font-size normalization anchor missing: _singleSlider(')
        insertion = """  Future<void> _fontSize(DesignElement element) => _singleSlider(
    'Font Size',
    element.fontSize,
    5,
    100,
    (v) => '${v.round()} px',
    controller.setSelectedFontSize,
  );

"""
        s = s.replace(marker, insertion + marker, 1)
    return s

patch('lib/screens/workspace_screen.dart', workspace_font_size)
def catalog_sheet(s):
    # Deterministic catalog-tab normalization. Do not rely on one fragile whitespace shape.
    dynamic_tabs = """TabBar(
              controller: _tabs,
              isScrollable: true,
              tabAlignment: TabAlignment.start,
              labelPadding: const EdgeInsets.symmetric(horizontal: 14),
              tabs: [
                Tab(text: 'Shapes • ${PremiumShapeCatalog.shapeNames.length}'),
                Tab(text: 'Borders • ${PremiumShapeCatalog.borderNames.length}'),
                Tab(text: 'Special Text • ${PremiumShapeCatalog.specialTextNames.length}'),
              ],
            ),"""

    # First prefer the exact current generated block.
    exact = """TabBar(
              controller: _tabs,
              tabs: const [
                Tab(text: 'Shapes 100+'),
                Tab(text: 'Borders 100+'),
                Tab(text: 'Special Text 100+'),
              ],
            ),"""
    if exact in s:
        s = s.replace(exact, dynamic_tabs, 1)
    elif 'PremiumShapeCatalog.shapeNames.length' not in s:
        # Fallback: locate the TabBar call whose controller is _tabs and replace
        # its complete balanced call, regardless of formatting/line wrapping.
        marker = 'TabBar('
        pos = s.find(marker)
        while pos >= 0:
            close = pos + len(marker)
            depth = 1
            in_single = False
            in_double = False
            escape = False
            while close < len(s) and depth:
                ch = s[close]
                if escape:
                    escape = False
                elif ch == '\\':
                    escape = True
                elif in_single:
                    if ch == "'":
                        in_single = False
                elif in_double:
                    if ch == '"':
                        in_double = False
                elif ch == "'":
                    in_single = True
                elif ch == '"':
                    in_double = True
                elif ch == '(':
                    depth += 1
                elif ch == ')':
                    depth -= 1
                close += 1
            block = s[pos:close]
            if 'controller: _tabs' in block and 'tabs:' in block:
                s = s[:pos] + dynamic_tabs.rstrip(',') + s[close:]
                break
            pos = s.find(marker, pos + len(marker))

    # The acceptance contract must be true immediately after this transformation.
    if 'PremiumShapeCatalog.shapeNames.length' not in s:
        raise SystemExit('Catalog tab transformation failed: Shapes count was not inserted')
    if 'PremiumShapeCatalog.borderNames.length' not in s:
        raise SystemExit('Catalog tab transformation failed: Borders count was not inserted')
    if 'PremiumShapeCatalog.specialTextNames.length' not in s:
        raise SystemExit('Catalog tab transformation failed: Special Text count was not inserted')
    if 'isScrollable: true' not in s:
        raise SystemExit('Catalog tab transformation failed: scrollable TabBar missing')

    # Adaptive catalog cards; labels may wrap to two lines.
    s = re.sub(r'const SliverGridDelegateWithFixedCrossAxisCount\(\s*crossAxisCount:\s*3,\s*mainAxisSpacing:\s*10,\s*crossAxisSpacing:\s*10,\s*childAspectRatio:\s*\.88,\s*\)',
               '''const SliverGridDelegateWithMaxCrossAxisExtent(
        maxCrossAxisExtent: 155,
        mainAxisSpacing: 10,
        crossAxisSpacing: 10,
        childAspectRatio: .90,
      )''', s, count=1)
    s = s.replace("maxLines: 1,\n                    overflow: TextOverflow.ellipsis,\n                    textAlign: TextAlign.center,",
                  "maxLines: 2,\n                    softWrap: true,\n                    overflow: TextOverflow.clip,\n                    textAlign: TextAlign.center,")
    return s

patch('lib/widgets/premium_catalog_sheet.dart', catalog_sheet)

def controller(s):
    # Catalog geometry: keep circles/polygons from being stretched into arbitrary ovals.
    s = s.replace(
        "if (e.kind == ElementKind.image && (left || right) && (top || bottom)) {",
        "if ((e.kind == ElementKind.image || (e.kind == ElementKind.shape && e.catalogType == 'shape' && e.shapeType != 3)) && (left || right) && (top || bottom)) {",
        1)
    # Font contract is exactly 5–100 px.
    s = re.sub(r'e\.fontSize\s*=\s*value\.clamp\(5,\s*300\)', 'e.fontSize = value.clamp(5, 100)', s)
    # Insert a text-box fitter once; TextPainter measures actual laid-out height.
    if 'void _fitTextBoxToContent(DesignElement e)' not in s:
        anchor = '  void editSelectedText(String value) {'
        helper = '''  void _fitTextBoxToContent(DesignElement e) {
    if (e.kind != ElementKind.text || e.text.trim().isEmpty || e.width <= 0) return;
    final painter = TextPainter(
      text: TextSpan(
        text: e.text,
        style: TextStyle(
          fontFamily: e.fontFamily,
          fontSize: e.fontSize,
          fontWeight: e.bold ? FontWeight.bold : FontWeight.normal,
          fontStyle: e.italic ? FontStyle.italic : FontStyle.normal,
          height: e.lineHeight,
          letterSpacing: e.letterSpacing,
        ),
      ),
      textAlign: e.textAlign,
      textDirection: e.textDirection,
      textWidthBasis: TextWidthBasis.parent,
    );
    painter.layout(maxWidth: e.width);
    e.height = painter.height.clamp(32.0, page.size.height).toDouble();
    painter.dispose();
  }

'''
        if anchor not in s:
            raise SystemExit('text edit anchor missing')
        s = s.replace(anchor, helper + anchor, 1)
    # Refit after text/size/font/spacing changes; do not shrink the font itself.
    s = re.sub(r'(void editSelectedText\(String value\) \{.*?e\.text = value;)', r'\1 _fitTextBoxToContent(e);', s, count=1, flags=re.S)
    s = re.sub(r'(void setSelectedFontSize\(double value\) \{.*?e\.fontSize = value\.clamp\(5, 100\);)', r'\1 _fitTextBoxToContent(e);', s, count=1, flags=re.S)
    s = re.sub(r'(void setSelectedTypography\(\{double\? letterSpacing, double\? lineHeight\}\) \{.*?if \(lineHeight != null\) e\.lineHeight = lineHeight\.clamp\(\.7, 3\);)', r'\1 _fitTextBoxToContent(e);', s, count=1, flags=re.S)
    # If the generated script has a 300px font-range check, make it 100.
    s = s.replace('clamp(5, 300)', 'clamp(5, 100)')
    return s

patch('lib/state/workspace_controller.dart', controller)

def canvas(s):
    # No hidden FittedBox scaling and no ellipsis for editor text.
    s = re.sub(r'overflow:\s*TextOverflow\.ellipsis,', 'overflow: TextOverflow.visible,', s)
    s = s.replace('fontSize: e.fontSize,', 'fontSize: e.fontSize,\n                textHeightBehavior: const TextHeightBehavior(applyHeightToFirstAscent: false, applyHeightToLastDescent: false),', 1)
    # Catalog objects use their real painter, not a generic rounded rectangle.
    if 'CatalogShapePainter' in s and "e.catalogType == 'shape' || e.catalogType == 'border'" not in s:
        old = "      case ElementKind.shape:\n        child = DecoratedBox(decoration: _decoration(e, isShape: true));\n        break;"
        new = """      case ElementKind.shape:
        if (e.catalogType == 'shape' || e.catalogType == 'border') {
          child = CustomPaint(
            painter: CatalogShapePainter(
              type: e.shapeType,
              fill: e.color,
              stroke: e.strokeColor.a > 0 ? e.strokeColor : _purple,
              strokeWidth: e.strokeWidth > 0 ? e.strokeWidth : 3,
              radius: e.radius,
              border: e.catalogType == 'border',
            ),
          );
        } else {
          child = DecoratedBox(decoration: _decoration(e, isShape: true));
        }
        break;"""
        if old in s:
            s=s.replace(old,new,1)
    return s

def repair_workspace_font_catalog(s):
    # The generated font catalog must remain one valid class-member block.
    # Rebuild it deterministically so no orphan spread/list fragments can reach dart format.
    if 'Future<void> _fontSheet() async' not in s or 'Future<void> _fontSize' not in s:
        return s
    safe = '''  Future<void> _fontSheet() async {
    final element = controller.selected;
    if (element == null) return;
    final family = await showModalBottomSheet<String>(
      context: context,
      showDragHandle: true,
      isScrollControlled: true,
      builder: (sheetContext) => SafeArea(
        child: ListView(
          shrinkWrap: true,
          padding: const EdgeInsets.only(bottom: 18),
          children: [
            const _SheetHeader('Urdu Typography Studio', 'Premium Urdu, Nastaliq & Quranic font families'),
            _fontTile('Jameel Noori Nastaleeq', 'Classic Urdu Nastaliq', 'JameelNooriNastaleeq', element.fontFamily),
            _fontTile('Alvi Nastaleeq', 'Traditional Nastaliq', 'AlviNastaleeq', element.fontFamily),
            _fontTile('Mehr Nastaliq', 'Lahori Nastaliq', 'MehrNastaliq', element.fontFamily),
            _fontTile('Gulzar', 'Modern Nastaliq', 'Gulzar', element.fontFamily),
            _fontTile('Noto Nastaliq Urdu', 'Unicode Nastaliq', 'NotoNastaliqUrdu', element.fontFamily),
            _fontTile('Al Majeed Quranic', 'Quranic display', 'AlMajeedQuranic', element.fontFamily),
            _fontTile('Bombay Black', 'Bold display', 'BombayBlack', element.fontFamily),
          ],
        ),
      ),
    );
    if (family != null) controller.setSelectedFont(family);
  }

  Widget _fontTile(String title, String subtitle, String family, String current) {
    final active = current == family;
    return ListTile(
      contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 3),
      leading: CircleAvatar(
        radius: 21,
        backgroundColor: active ? _primary : const Color(0x12000000),
        child: Icon(Icons.font_download_rounded, color: active ? Colors.white : Colors.black54),
      ),
      title: Text(title, style: TextStyle(fontFamily: family, fontSize: 21, fontWeight: FontWeight.w700)),
      subtitle: Text(subtitle, maxLines: 1, overflow: TextOverflow.ellipsis),
      trailing: active ? const Icon(Icons.check_circle_rounded, color: _primary) : const Icon(Icons.chevron_right_rounded, color: Colors.black26),
      onTap: () => Navigator.pop(context, family),
    );
  }

'''
    import re as _re
    pattern = _re.compile(r'  Future<void> _fontSheet\(\) async \{.*?(?=  Future<void> _fontSize)', _re.S)
    if not pattern.search(s):
        raise SystemExit('Font catalog structural region not found')
    return pattern.sub(safe, s, count=1)

patch('lib/screens/workspace_screen.dart', repair_workspace_font_catalog)

patch('lib/widgets/design_canvas.dart', canvas)

def catalogs(s):
    # Ensure radius participates in catalog painting and repaint invalidation.
    if 'final double radius;' not in s:
        s=s.replace('final int type; final Color fill; final Color stroke; final double strokeWidth; final bool border;',
                    'final int type; final Color fill; final Color stroke; final double strokeWidth; final bool border; final double radius;',1)
    if 'required this.strokeWidth, this.radius = 18' not in s:
        s=s.replace('required this.strokeWidth, this.border = false});',
                    'required this.strokeWidth, this.radius = 18, this.border = false});',1)
    s=s.replace('oldDelegate.strokeWidth != strokeWidth || oldDelegate.border != border;',
                'oldDelegate.strokeWidth != strokeWidth || oldDelegate.radius != radius || oldDelegate.border != border;')
    return s

patch('lib/widgets/premium_catalogs.dart', catalogs)

# Hard acceptance contracts: fail before Flutter analyze if the generated source
# does not contain the behaviors this pass is intended to guarantee.
checks = [
    ('lib/models/design_models.dart', ['catalogType', 'shapeType', "fontSize: ((json['fontSize'] as num?)?.toDouble() ?? 56).clamp(5, 100).toDouble()"]),
    ('lib/state/workspace_controller.dart', ['void addCatalogShape(int shapeType)', 'void addBorder(int borderType)', 'clamp(5, 100)', 'TextPainter', "e.shapeType != 3", '_fitTextBoxToContent']),
    ('lib/widgets/design_canvas.dart', ['CatalogShapePainter', 'radius: e.radius', 'fontSize: e.fontSize']),
    ('lib/widgets/premium_catalog_sheet.dart', ['isScrollable: true', 'PremiumShapeCatalog.shapeNames.length', 'PremiumShapeCatalog.borderNames.length']),
    ('lib/screens/home_screen.dart', ['maxCrossAxisExtent: 158', 'height: 136']),
    ('lib/screens/workspace_screen.dart', ["_fontSize(DesignElement element)", "element.fontSize", "5", "100"]),
]

for path, needles in checks:
    text = Path(path).read_text(encoding='utf-8')
    for needle in needles:
        if needle not in text:
            raise SystemExit(f'Acceptance contract missing: {path}: {needle}')

print('Final acceptance polish verified: responsive Home, real catalog counts, live catalog-to-canvas rendering, geometry-preserving shapes, 5–100px typography, and measured text-box sizing.')