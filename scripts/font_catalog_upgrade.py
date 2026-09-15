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
              const Padding(padding: EdgeInsets.fromLTRB(20, 8, 20, 6), child: Text('Nastaliq Collection', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w900, color: Colors.black54))),
              _fontTile('Jameel Noori Nastaleeq', 'Classic • authentic Urdu Nastaliq', 'JameelNooriNastaleeq', element.fontFamily),
              _fontTile('Alvi Nastaleeq', 'Elegant • traditional Nastaliq', 'AlviNastaleeq', element.fontFamily),
              _fontTile('Mehr Nastaliq Web', 'Clean • fast Lahori Nastaliq', 'MehrNastaliq', element.fontFamily),
              _fontTile('Gulzar', 'Modern • expressive Nastaliq', 'Gulzar', element.fontFamily),
              _fontTile('Noto Nastaliq Urdu', 'Balanced • Unicode Nastaliq', 'NotoNastaliqUrdu', element.fontFamily),
              const Padding(padding: EdgeInsets.fromLTRB(20, 16, 20, 6), child: Text('Quranic & Display', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w900, color: Colors.black54))),
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
      leading: CircleAvatar(radius: 21, backgroundColor: active ? _primary : const Color(0x12000000), child: Icon(Icons.font_download_rounded, color: active ? Colors.white : Colors.black54)),
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
      if (originalSelection != null && controller.elements.any((e) => e.id == originalSelection)) controller.select(originalSelection);
      if (mounted) setState(() {});
    }
  }

'''

COMPOSER = r'''  Future<String?> _textDialog(String title, String initial, {String fontFamily = 'JameelNooriNastaleeq'}) async {
    final textController = TextEditingController(text: initial);
    var selectedFont = fontFamily;
    var fontSize = 30.0;
    var bold = false;
    var italic = false;
    var textAlign = TextAlign.right;
    var activePanel = 'Font';

    final result = await showDialog<String>(
      context: context,
      barrierColor: Colors.black54,
      builder: (dialogContext) {
        return Dialog(
          insetPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 16),
          backgroundColor: Colors.transparent,
          child: StatefulBuilder(
            builder: (context, setState) {
              final media = MediaQuery.of(context);
              final maxHeight = media.size.height - media.viewInsets.bottom - 24;
              return ConstrainedBox(
                constraints: BoxConstraints(maxWidth: 620, maxHeight: maxHeight.clamp(420.0, 900.0).toDouble()),
                child: Material(
                  color: Colors.white,
                  elevation: 18,
                  shadowColor: Colors.black45,
                  borderRadius: BorderRadius.circular(28),
                  clipBehavior: Clip.antiAlias,
                  child: Column(
                    children: [
                      Container(
                        padding: const EdgeInsets.fromLTRB(18, 15, 10, 13),
                        decoration: const BoxDecoration(gradient: LinearGradient(colors: [Color(0xFF4C1D95), Color(0xFF7C3AED)], begin: Alignment.topLeft, end: Alignment.bottomRight)),
                        child: Row(children: [
                          Container(width: 44, height: 44, decoration: BoxDecoration(color: Colors.white.withValues(alpha: .16), borderRadius: BorderRadius.circular(14)), child: const Icon(Icons.text_fields_rounded, color: Colors.white, size: 25)),
                          const SizedBox(width: 12),
                          Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(title, style: const TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.w900)), const SizedBox(height: 2), const Text('Urdu Typography Composer', style: TextStyle(color: Color(0xD9FFFFFF), fontSize: 11, fontWeight: FontWeight.w600))])),
                          IconButton(onPressed: () => Navigator.pop(dialogContext), icon: const Icon(Icons.close_rounded, color: Colors.white)),
                        ]),
                      ),
                      Flexible(
                        child: SingleChildScrollView(
                          padding: const EdgeInsets.fromLTRB(14, 14, 14, 8),
                          child: Column(children: [
                            Container(
                              width: double.infinity,
                              constraints: const BoxConstraints(minHeight: 150),
                              decoration: BoxDecoration(color: const Color(0xFFF8F7FF), borderRadius: BorderRadius.circular(22), border: Border.all(color: _primary.withValues(alpha: .35), width: 1.5), boxShadow: const [BoxShadow(color: Color(0x0D000000), blurRadius: 16, offset: Offset(0, 5))]),
                              child: TextField(
                                controller: textController,
                                autofocus: true,
                                minLines: 5,
                                maxLines: 9,
                                textDirection: TextDirection.rtl,
                                textAlign: textAlign,
                                textInputAction: TextInputAction.newline,
                                keyboardType: TextInputType.multiline,
                                style: TextStyle(fontFamily: selectedFont, fontSize: fontSize, height: 1.45, fontWeight: bold ? FontWeight.w700 : FontWeight.w400, fontStyle: italic ? FontStyle.italic : FontStyle.normal, color: const Color(0xFF171329)),
                                decoration: const InputDecoration(hintText: 'اپنا خوبصورت اردو متن یہاں لکھیں…', hintStyle: TextStyle(color: Colors.black38, fontSize: 19), border: InputBorder.none, contentPadding: EdgeInsets.fromLTRB(18, 18, 18, 18)),
                              ),
                            ),
                            const SizedBox(height: 12),
                            SizedBox(
                              height: 46,
                              child: ListView(scrollDirection: Axis.horizontal, children: ['Font', 'Size', 'Style', 'Align'].map((panel) {
                                final active = activePanel == panel;
                                return Padding(padding: const EdgeInsets.only(right: 7), child: ChoiceChip(selected: active, label: Text(panel, style: TextStyle(fontWeight: FontWeight.w800, color: active ? Colors.white : Colors.black87)), avatar: Icon(panel == 'Font' ? Icons.font_download_rounded : panel == 'Size' ? Icons.format_size_rounded : panel == 'Style' ? Icons.auto_awesome_rounded : Icons.format_align_right_rounded, size: 18, color: active ? Colors.white : _primary), selectedColor: _primary, backgroundColor: const Color(0xFFF1EFF8), onSelected: (_) => setState(() => activePanel = panel)));
                              }).toList()),
                            ),
                            const SizedBox(height: 8),
                            if (activePanel == 'Font') _composerFontPanel(selectedFont, (font) => setState(() => selectedFont = font))
                            else if (activePanel == 'Size') _composerSizePanel(fontSize, (size) => setState(() => fontSize = size))
                            else if (activePanel == 'Style') _composerStylePanel(bold, italic, (v) => setState(() => bold = v), (v) => setState(() => italic = v))
                            else _composerAlignPanel(textAlign, (align) => setState(() => textAlign = align)),
                          ]),
                        ),
                      ),
                      Container(padding: const EdgeInsets.fromLTRB(14, 10, 14, 14), decoration: const BoxDecoration(color: Color(0xFFFCFBFF), border: Border(top: BorderSide(color: Color(0x10000000)))), child: Row(children: [Expanded(child: OutlinedButton.icon(onPressed: () => Navigator.pop(dialogContext), icon: const Icon(Icons.close_rounded), label: const Text('Cancel'))), const SizedBox(width: 10), Expanded(child: FilledButton.icon(onPressed: () => Navigator.pop(dialogContext, textController.text), icon: const Icon(Icons.check_rounded), label: const Text('Apply')))])),
                    ],
                  ),
                ),
              );
            },
          ),
        );
      },
    );
    textController.dispose();
    return result;
  }

  Widget _composerFontPanel(String current, ValueChanged<String> onChanged) {
    const fonts = [('Jameel Noori', 'JameelNooriNastaleeq'), ('Alvi Nastaleeq', 'AlviNastaleeq'), ('Mehr Nastaliq', 'MehrNastaliq'), ('Gulzar', 'Gulzar'), ('Noto Nastaliq', 'NotoNastaliqUrdu'), ('Al Majeed', 'AlMajeedQuranic'), ('Bombay Black', 'BombayBlack')];
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [const Padding(padding: EdgeInsets.fromLTRB(4, 0, 4, 8), child: Text('Font Family', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w900, color: Colors.black54))), SizedBox(height: 88, child: ListView.separated(scrollDirection: Axis.horizontal, itemCount: fonts.length, separatorBuilder: (_, __) => const SizedBox(width: 8), itemBuilder: (context, index) { final font = fonts[index]; final active = current == font.$2; return InkWell(onTap: () => onChanged(font.$2), borderRadius: BorderRadius.circular(16), child: AnimatedContainer(duration: const Duration(milliseconds: 160), width: 116, padding: const EdgeInsets.all(9), decoration: BoxDecoration(color: active ? _primary.withValues(alpha: .08) : Colors.white, borderRadius: BorderRadius.circular(16), border: Border.all(color: active ? _primary : const Color(0x16000000), width: active ? 1.7 : 1)), child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [Expanded(child: FittedBox(fit: BoxFit.scaleDown, child: Text('اردو', style: TextStyle(fontFamily: font.$2, fontSize: 30, color: _primary, fontWeight: FontWeight.w700)))), const SizedBox(height: 4), Text(font.$1, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w800))]))); })))],);
  }

  Widget _composerSizePanel(double value, ValueChanged<double> onChanged) {
    return _composerPanelCard('Font Size', Row(children: [_roundComposerButton(Icons.remove_rounded, () => onChanged((value - 2).clamp(8, 300).toDouble())), Expanded(child: Slider(min: 8, max: 300, value: value, onChanged: onChanged)), _roundComposerButton(Icons.add_rounded, () => onChanged((value + 2).clamp(8, 300).toDouble())), const SizedBox(width: 8), Text('${value.round()} px', style: const TextStyle(fontWeight: FontWeight.w900, color: _primary))]));
  }

  Widget _composerStylePanel(bool bold, bool italic, ValueChanged<bool> onBold, ValueChanged<bool> onItalic) => Row(children: [Expanded(child: _composerToggle(Icons.format_bold_rounded, 'Bold', bold, onBold)), const SizedBox(width: 8), Expanded(child: _composerToggle(Icons.format_italic_rounded, 'Italic', italic, onItalic))]);

  Widget _composerAlignPanel(TextAlign value, ValueChanged<TextAlign> onChanged) => _composerPanelCard('Alignment', Row(children: [Expanded(child: _composerToggle(Icons.format_align_right_rounded, 'Right', value == TextAlign.right, (_) => onChanged(TextAlign.right))), const SizedBox(width: 8), Expanded(child: _composerToggle(Icons.format_align_center_rounded, 'Center', value == TextAlign.center, (_) => onChanged(TextAlign.center))), const SizedBox(width: 8), Expanded(child: _composerToggle(Icons.format_align_left_rounded, 'Left', value == TextAlign.left, (_) => onChanged(TextAlign.left)))]));

  Widget _composerPanelCard(String title, Widget child) => Container(width: double.infinity, padding: const EdgeInsets.fromLTRB(12, 10, 12, 10), decoration: BoxDecoration(color: const Color(0xFFF8F7FC), borderRadius: BorderRadius.circular(18)), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(title, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w900)), const SizedBox(height: 4), child]));

  Widget _roundComposerButton(IconData icon, VoidCallback onTap) => IconButton.filledTonal(onPressed: onTap, icon: Icon(icon, size: 19), visualDensity: VisualDensity.compact);

  Widget _composerToggle(IconData icon, String label, bool active, ValueChanged<bool> onChanged) => InkWell(onTap: () => onChanged(!active), borderRadius: BorderRadius.circular(16), child: AnimatedContainer(duration: const Duration(milliseconds: 150), padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12), decoration: BoxDecoration(color: active ? _primary.withValues(alpha: .10) : const Color(0xFFF7F5FA), borderRadius: BorderRadius.circular(16), border: Border.all(color: active ? _primary : const Color(0x10000000))), child: Row(mainAxisAlignment: MainAxisAlignment.center, children: [Icon(icon, size: 20, color: active ? _primary : Colors.black54), const SizedBox(width: 7), Text(label, style: TextStyle(fontWeight: FontWeight.w800, color: active ? _primary : Colors.black87))])));

'''

text = WORKSPACE.read_text(encoding='utf-8')
new_text, count = re.subn(r"  Future<void> _fontSheet\(\) async \{.*?\n  Future<void> _fontSize", FONT_SHEET + "  Future<void> _fontSize", text, count=1, flags=re.S)
if count != 1: raise SystemExit('Could not locate the font sheet section.')
new_text = new_text.replace("fontFamily == 'JameelNoori' ? 'Gulzar' : fontFamily", "fontFamily")
new_text = new_text.replace("fontFamily: 'Gulzar', fontSize: 23", "fontFamily: 'JameelNooriNastaleeq', fontSize: 23")
new_text = new_text.replace("import 'package:flutter/material.dart';", "import 'dart:typed_data';\n\nimport 'package:flutter/material.dart';")
new_text, count = re.subn(r"  Future<String\?> _textDialog\(String title, String initial\) async \{.*?\n  \}\n\n  Future<void> _fontSheet", COMPOSER + "  Future<void> _fontSheet", new_text, count=1, flags=re.S)
if count != 1: raise SystemExit('Could not locate the text composer section.')
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
new_text, count = re.subn(r"  Future<void> _exportMenu\(String value\) async \{.*?\n  \}\n", PDF_EXPORT + export_method, new_text, count=1, flags=re.S)
if count != 1: raise SystemExit('Could not locate the export menu section.')
WORKSPACE.write_text(new_text, encoding='utf-8')
canvas = CANVAS.read_text(encoding='utf-8')
canvas = canvas.replace("fontFamily: e.fontFamily == 'JameelNoori' ? 'Gulzar' : e.fontFamily,", "fontFamily: e.fontFamily,")
CANVAS.write_text(canvas, encoding='utf-8')
print('Applied premium Urdu font catalog, rendered multi-page PDF export, and premium Urdu text composer.')
