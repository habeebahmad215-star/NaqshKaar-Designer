from pathlib import Path
import re

WORKSPACE = Path('lib/screens/workspace_screen.dart')
CANVAS = Path('lib/widgets/design_canvas.dart')

FONT_SHEET = r'''  Future<void> _fontSheet() async {
    final element = controller.selected;
    if (element == null) return;
    final family = await showModalBottomSheet<String>(
      context: context,
      showDragHandle: true,
      isScrollControlled: true,
      builder: (sheetContext) {
        return SafeArea(
          child: ListView(
            shrinkWrap: true,
            padding: const EdgeInsets.only(bottom: 18),
            children: [
              const _SheetHeader('Urdu Typography Studio', 'Premium Urdu, Nastaliq & Quranic font families'),
              const Padding(
                padding: EdgeInsets.fromLTRB(20, 8, 20, 6),
                child: Text('Nastaliq Collection', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w900, color: Colors.black54)),
              ),
              _fontTile('Jameel Noori Nastaleeq', 'Classic • authentic Urdu Nastaliq', 'JameelNooriNastaleeq', element.fontFamily),
              _fontTile('Alvi Nastaleeq', 'Elegant • traditional Nastaliq', 'AlviNastaleeq', element.fontFamily),
              _fontTile('Mehr Nastaliq Web', 'Clean • fast Lahori Nastaliq', 'MehrNastaliq', element.fontFamily),
              _fontTile('Gulzar', 'Modern • expressive Nastaliq', 'Gulzar', element.fontFamily),
              _fontTile('Noto Nastaliq Urdu', 'Balanced • Unicode Nastaliq', 'NotoNastaliqUrdu', element.fontFamily),
              const Padding(
                padding: EdgeInsets.fromLTRB(20, 16, 20, 6),
                child: Text('Quranic & Display', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w900, color: Colors.black54)),
              ),
              _fontTile('Al Majeed Quranic Font', 'Quranic • ornamental Arabic display', 'AlMajeedQuranic', element.fontFamily),
              _fontTile('Bombay Black Unicode', 'Bold • high-impact display', 'BombayBlack', element.fontFamily),
            ],
          ),
        );
      },
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

text = WORKSPACE.read_text(encoding='utf-8')
new_text, count = re.subn(
    r"  Future<void> _fontSheet\(\) async \{.*?\n  Future<void> _fontSize",
    FONT_SHEET + "  Future<void> _fontSize",
    text,
    count=1,
    flags=re.S,
)
if count != 1:
    raise SystemExit('Could not locate the font sheet section.')
new_text = new_text.replace("fontFamily == 'JameelNoori' ? 'Gulzar' : fontFamily", "fontFamily")
new_text = new_text.replace("fontFamily: 'Gulzar', fontSize: 23", "fontFamily: 'JameelNooriNastaleeq', fontSize: 23")
WORKSPACE.write_text(new_text, encoding='utf-8')

canvas = CANVAS.read_text(encoding='utf-8')
canvas = canvas.replace("fontFamily: e.fontFamily == 'JameelNoori' ? 'Gulzar' : e.fontFamily,", "fontFamily: e.fontFamily,")
CANVAS.write_text(canvas, encoding='utf-8')
print('Applied premium Urdu font catalog to workspace and canvas.')
