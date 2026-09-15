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

PDF_EXPORT = r'''  Future<void> _exportRenderedPdf() async {
    final originalPage = controller.currentPageIndex;
    final originalSelection = controller.selectedId;
    final pagePngs = <Uint8List>[];
    try {
      for (var i = 0; i < controller.project.pages.length; i++) {
        controller.switchPage(i);
        await WidgetsBinding.instance.endOfFrame;
        final page = controller.page;
        pagePngs.add(await _export.capturePng(_canvasKey, page.size.width, page.size.width));
      }
      await _export.shareRenderedPdf(project: controller.project, pagePngs: pagePngs);
    } finally {
      controller.switchPage(originalPage);
      if (originalSelection != null && controller.elements.any((e) => e.id == originalSelection)) {
        controller.select(originalSelection);
      }
      if (mounted) setState(() {});
    }
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

# The model-based PDF path was clipping Urdu Nastaliq in the Android PDF renderer.
# Use the already-rendered Flutter canvas for every project page instead.
new_text = new_text.replace("import 'package:flutter/material.dart';", "import 'dart:typed_data';\n\nimport 'package:flutter/material.dart';")
export_method = r'''  Future<void> _exportMenu(String value) async {
    try {
      if (value == 'pdf') {
        await _exportRenderedPdf();
      } else if (value == 'png') {
        await _export.exportPng(controller.page, _canvasKey);
      } else {
        await _export.exportJpg(controller.page, _canvasKey);
      }
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(value == 'pdf' ? 'PDF ready to share' : 'Export saved to gallery')));
    } catch (error) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Export failed: $error')));
    }
  }
'''
new_text, count = re.subn(
    r"  Future<void> _exportMenu\(String value\) async \{.*?\n  \}\n",
    PDF_EXPORT + export_method,
    new_text,
    count=1,
    flags=re.S,
)
if count != 1:
    raise SystemExit('Could not locate the export menu section.')
WORKSPACE.write_text(new_text, encoding='utf-8')

canvas = CANVAS.read_text(encoding='utf-8')
canvas = canvas.replace("fontFamily: e.fontFamily == 'JameelNoori' ? 'Gulzar' : e.fontFamily,", "fontFamily: e.fontFamily,")
CANVAS.write_text(canvas, encoding='utf-8')
print('Applied premium Urdu font catalog and rendered multi-page PDF export integration.')
