from pathlib import Path

W = Path('lib/screens/workspace_screen.dart')
w = W.read_text(encoding='utf-8')

# Replace the generated live-preview text dialog with a focused, premium composer.
start = w.index('  Future<String?> _textDialog(')
end = w.index('\n  Future<void> _fontSheet()', start)
text_method = r'''  Future<String?> _textDialog(String title, String initial) async {
    final textController = TextEditingController(text: initial);
    final focusNode = FocusNode();
    var direction = TextDirection.rtl;
    var fontFamily = 'JameelNooriNastaleeq';
    var textAlign = TextAlign.right;
    final editing = controller.selected?.kind == ElementKind.text && initial == controller.selected?.text;

    void insertAtCursor(String value) {
      final selection = textController.selection;
      final startOffset = selection.isValid ? selection.start : textController.text.length;
      final endOffset = selection.isValid ? selection.end : startOffset;
      final next = textController.text.replaceRange(startOffset, endOffset, value);
      textController.value = TextEditingValue(
        text: next,
        selection: TextSelection.collapsed(offset: startOffset + value.length),
      );
    }

    void smartClean() {
      final cleaned = textController.text
          .replaceAll(RegExp(r'[ \\t]+'), ' ')
          .replaceAll(RegExp(r'\\n{3,}'), '\\n\\n')
          .trim();
      textController.value = TextEditingValue(
        text: cleaned,
        selection: TextSelection.collapsed(offset: cleaned.length),
      );
    }

    final result = await showModalBottomSheet<String>(
      context: context,
      isScrollControlled: true,
      showDragHandle: false,
      backgroundColor: Colors.transparent,
      barrierColor: Colors.black54,
      builder: (sheetContext) {
        return StatefulBuilder(
          builder: (context, setSheetState) {
            final bottom = MediaQuery.viewInsetsOf(context).bottom;
            return Container(
              decoration: const BoxDecoration(
                color: Color(0xFFF8F8FB),
                borderRadius: BorderRadius.vertical(top: Radius.circular(30)),
              ),
              child: SafeArea(
                top: false,
                child: Padding(
                  padding: EdgeInsets.fromLTRB(14, 10, 14, 12 + bottom),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Container(width: 52, height: 5, decoration: BoxDecoration(color: const Color(0xFFD7D8DF), borderRadius: BorderRadius.circular(8))),
                      const SizedBox(height: 12),
                      Row(
                        children: [
                          _composerIconButton(Icons.keyboard_arrow_down_rounded, 'Close', () => Navigator.pop(sheetContext)),
                          const SizedBox(width: 10),
                          Expanded(
                            child: Container(
                              height: 52,
                              padding: const EdgeInsets.all(4),
                              decoration: BoxDecoration(color: const Color(0xFFEDEEF3), borderRadius: BorderRadius.circular(17)),
                              child: Row(
                                children: [
                                  Expanded(child: _composerLanguageButton('English', direction == TextDirection.ltr, () => setSheetState(() { direction = TextDirection.ltr; textAlign = TextAlign.left; }))),
                                  Expanded(child: _composerLanguageButton('اردو', direction == TextDirection.rtl, () => setSheetState(() { direction = TextDirection.rtl; textAlign = TextAlign.right; }))),
                                ],
                              ),
                            ),
                          ),
                          const SizedBox(width: 10),
                          _composerIconButton(Icons.menu_book_rounded, 'Font', () async {
                            final picked = await _composerFontPicker(context, fontFamily);
                            if (picked != null) setSheetState(() => fontFamily = picked);
                          }),
                        ],
                      ),
                      const SizedBox(height: 12),
                      Container(
                        width: double.infinity,
                        constraints: const BoxConstraints(minHeight: 205, maxHeight: 300),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(22),
                          border: Border.all(color: const Color(0xFF4C8BF5), width: 1.6),
                          boxShadow: const [BoxShadow(blurRadius: 22, offset: Offset(0, 8), color: Color(0x12000000))],
                        ),
                        child: Stack(
                          children: [
                            TextField(
                              controller: textController,
                              focusNode: focusNode,
                              autofocus: true,
                              expands: true,
                              maxLines: null,
                              minLines: null,
                              textDirection: direction,
                              textAlign: textAlign,
                              textInputAction: TextInputAction.newline,
                              cursorColor: _primary,
                              style: TextStyle(fontFamily: fontFamily, fontSize: 27, height: 1.45, color: Colors.black87),
                              decoration: const InputDecoration(border: InputBorder.none, contentPadding: EdgeInsets.fromLTRB(18, 18, 18, 58), hintText: 'اپنا متن یہاں لکھیں', hintStyle: TextStyle(color: Color(0xFFB9BBC3))),
                            ),
                            Positioned(
                              left: 12,
                              bottom: 10,
                              child: Material(
                                color: const Color(0xFFF4F5F8),
                                shape: const CircleBorder(),
                                child: IconButton(
                                  tooltip: 'Show keyboard',
                                  onPressed: () => focusNode.requestFocus(),
                                  icon: const Icon(Icons.keyboard_rounded, color: Color(0xFF646873)),
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 10),
                      SizedBox(
                        height: 68,
                        child: ListView(
                          scrollDirection: Axis.horizontal,
                          children: [
                            _composerAction(Icons.content_paste_rounded, 'Paste', () async {
                              final data = await Clipboard.getData(Clipboard.kTextPlain);
                              if (data?.text != null && data!.text!.isNotEmpty) insertAtCursor(data.text!);
                              focusNode.requestFocus();
                            }),
                            _composerAction(Icons.delete_sweep_rounded, 'Clear', () {
                              textController.clear();
                              focusNode.requestFocus();
                            }),
                            _composerAction(Icons.auto_awesome_rounded, 'Smart', () => _composerSmartTools(context, textController, insertAtCursor, smartClean)),
                            _composerAction(Icons.translate_rounded, 'Translate', () => _composerTranslate(context, textController.text, direction)),
                            _composerAction(Icons.grid_view_rounded, 'Huroof', () => _composerHuroof(context, insertAtCursor)),
                            _composerAction(Icons.format_align_center_rounded, 'Align', () => _composerAlignment(context, textAlign, (value) => setSheetState(() => textAlign = value))),
                          ],
                        ),
                      ),
                      const SizedBox(height: 6),
                      Row(
                        children: [
                          Expanded(
                            child: OutlinedButton(
                              onPressed: () => Navigator.pop(sheetContext),
                              style: OutlinedButton.styleFrom(minimumSize: const Size.fromHeight(58), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(17)), backgroundColor: const Color(0xFFF1F2F5), side: BorderSide.none),
                              child: const Text('Cancel', style: TextStyle(fontSize: 17, fontWeight: FontWeight.w800, color: Color(0xFF6A6D78))),
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            flex: 2,
                            child: FilledButton.icon(
                              onPressed: () => Navigator.pop(sheetContext, textController.text),
                              style: FilledButton.styleFrom(minimumSize: const Size.fromHeight(58), backgroundColor: const Color(0xFF22C55E), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(17))),
                              icon: const Icon(Icons.check_rounded),
                              label: Text(editing ? 'Update design' : 'Add to design', style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w900)),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            );
          },
        );
      },
    );
    focusNode.dispose();
    textController.dispose();
    return result;
  }

  Widget _composerIconButton(IconData icon, String tooltip, VoidCallback onTap) {
    return Material(
      color: Colors.white,
      borderRadius: BorderRadius.circular(16),
      child: IconButton(tooltip: tooltip, onPressed: onTap, icon: Icon(icon, size: 26, color: const Color(0xFF565962))),
    );
  }

  Widget _composerLanguageButton(String label, bool active, VoidCallback onTap) {
    return Material(
      color: active ? Colors.white : Colors.transparent,
      borderRadius: BorderRadius.circular(14),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(14),
        child: Center(child: Text(label, style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: active ? const Color(0xFF24262D) : const Color(0xFF9699A3)))),
      ),
    );
  }

  Widget _composerAction(IconData icon, String label, VoidCallback onTap) {
    return SizedBox(
      width: 76,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(14),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 25, color: const Color(0xFF555861)),
            const SizedBox(height: 5),
            Text(label, maxLines: 1, style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: Color(0xFF555861))),
          ],
        ),
      ),
    );
  }

  Future<String?> _composerFontPicker(BuildContext context, String current) {
    const fonts = [
      ('Jameel Noori Nastaleeq', 'JameelNooriNastaleeq'),
      ('Mehr Nastaliq', 'MehrNastaliq'),
      ('Alvi Nastaleeq', 'AlviNastaleeq'),
      ('Gulzar', 'Gulzar'),
      ('Noto Nastaliq Urdu', 'NotoNastaliqUrdu'),
      ('Al Majeed Quranic', 'AlMajeedQuranic'),
      ('Bombay Black', 'BombayBlack'),
    ];
    return showModalBottomSheet<String>(
      context: context,
      showDragHandle: true,
      backgroundColor: const Color(0xFFF8F8FB),
      builder: (sheetContext) => SafeArea(
        child: ListView(
          shrinkWrap: true,
          children: [
            const _SheetHeader('Font', 'Jameel Noori Nastaleeq is the default'),
            ...fonts.map((font) => ListTile(
              leading: CircleAvatar(backgroundColor: font.$2 == current ? _primary : const Color(0xFFE9E9EF), child: Icon(Icons.font_download_rounded, color: font.$2 == current ? Colors.white : Colors.black54)),
              title: Text(font.$1, style: TextStyle(fontFamily: font.$2, fontSize: 20, fontWeight: FontWeight.w700)),
              trailing: font.$2 == current ? const Icon(Icons.check_circle_rounded, color: _primary) : null,
              onTap: () => Navigator.pop(sheetContext, font.$2),
            )),
          ],
        ),
      ),
    );
  }

  Future<void> _composerSmartTools(BuildContext context, TextEditingController controller, void Function(String) insertAtCursor, VoidCallback clean) async {
    await showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      builder: (sheetContext) => SafeArea(
        child: Wrap(
          children: [
            const _SheetHeader('Smart Text', 'Useful local editing tools — no dummy actions'),
            ListTile(leading: const Icon(Icons.cleaning_services_rounded), title: const Text('Clean spaces & line breaks'), onTap: () { clean(); Navigator.pop(sheetContext); }),
            ListTile(leading: const Icon(Icons.format_quote_rounded), title: const Text('Add Urdu punctuation'), onTap: () { controller.text = controller.text.replaceAll(',', '،').replaceAll('?', '؟'); Navigator.pop(sheetContext); }),
            ListTile(leading: const Icon(Icons.auto_awesome_rounded), title: const Text('Insert Bismillah'), onTap: () { insertAtCursor('بِسْمِ اللّٰهِ الرَّحْمٰنِ الرَّحِیْمِ\n'); Navigator.pop(sheetContext); }),
          ],
        ),
      ),
    );
  }

  Future<void> _composerTranslate(BuildContext context, String text, TextDirection direction) async {
    if (text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Type some text first')));
      return;
    }
    final source = direction == TextDirection.rtl ? 'ur' : 'en';
    final target = source == 'ur' ? 'en' : 'ur';
    final uri = Uri.https('translate.google.com', '/', {'sl': source, 'tl': target, 'text': text});
    await Clipboard.setData(ClipboardData(text: text));
    if (!context.mounted) return;
    await showDialog<void>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Translate'),
        content: const Text('Text copied to clipboard. Open Google Translate to translate it.'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(dialogContext), child: const Text('Close')),
          FilledButton(onPressed: () async { Navigator.pop(dialogContext); await _openExternalUri(uri); }, child: const Text('Open Translate')),
        ],
      ),
    );
  }

  Future<void> _openExternalUri(Uri uri) async {
    try {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    } catch (_) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Could not open the translation service')));
    }
  }

  Future<void> _composerHuroof(BuildContext context, void Function(String) insertAtCursor) async {
    const groups = [
      ('Harakaat', ['َ', 'ِ', 'ُ', 'ً', 'ٍ', 'ٌ', 'ْ', 'ّ', 'ٰ']),
      ('Urdu', ['۔', '،', '؟', '؛', 'ء', 'ئ', 'ؤ', 'ے', 'ں', 'ﷺ', 'ؓ', 'ؒ']),
      ('Arabic', ['ٱ', 'أ', 'إ', 'آ', 'ة', 'ى', 'ـ', '۝', '۞']),
    ];
    await showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      builder: (sheetContext) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(16, 8, 16, 20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const _SheetHeader('Huroof & Symbols', 'Insert a character at the current cursor'),
              ...groups.map((group) => Padding(
                padding: const EdgeInsets.only(bottom: 10),
                child: Wrap(spacing: 8, runSpacing: 8, children: [
                  ...group.$2.map((symbol) => OutlinedButton(onPressed: () { insertAtCursor(symbol); Navigator.pop(sheetContext); }, child: Text(symbol, style: const TextStyle(fontSize: 21)))),
                ]),
              )),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _composerAlignment(BuildContext context, TextAlign current, ValueChanged<TextAlign> apply) async {
    final selected = await showModalBottomSheet<TextAlign>(
      context: context,
      showDragHandle: true,
      builder: (sheetContext) => SafeArea(
        child: Wrap(
          children: [
            const _SheetHeader('Alignment', 'Choose how the text sits in the composer'),
            ListTile(leading: const Icon(Icons.format_align_left_rounded), title: const Text('Left'), onTap: () => Navigator.pop(sheetContext, TextAlign.left)),
            ListTile(leading: const Icon(Icons.format_align_center_rounded), title: const Text('Center'), onTap: () => Navigator.pop(sheetContext, TextAlign.center)),
            ListTile(leading: const Icon(Icons.format_align_right_rounded), title: const Text('Right'), onTap: () => Navigator.pop(sheetContext, TextAlign.right)),
            ListTile(leading: const Icon(Icons.format_align_justify_rounded), title: const Text('Justify'), onTap: () => Navigator.pop(sheetContext, TextAlign.justify)),
          ],
        ),
      ),
    );
    if (selected != null) apply(selected);
  }
'''
w = w[:start] + text_method + w[end:]

# Replace the old limited font picker so Jameel and every bundled font are selectable.
start = w.index('  Future<void> _fontSheet()')
end = w.index('\n  Widget _fontTile(', start)
font_method = r'''  Future<void> _fontSheet() async {
    final element = controller.selected;
    if (element == null) return;
    const fonts = [
      ('Jameel Noori Nastaleeq', 'JameelNooriNastaleeq', 'Default premium Urdu font'),
      ('Mehr Nastaliq', 'MehrNastaliq', 'Traditional Nastaliq'),
      ('Alvi Nastaleeq', 'AlviNastaleeq', 'Classic Urdu style'),
      ('Gulzar', 'Gulzar', 'Contemporary Nastaliq'),
      ('Noto Nastaliq Urdu', 'NotoNastaliqUrdu', 'Unicode Nastaliq'),
      ('Al Majeed Quranic', 'AlMajeedQuranic', 'Quranic typography'),
      ('Bombay Black', 'BombayBlack', 'Bold display style'),
    ];
    final family = await showModalBottomSheet<String>(
      context: context,
      showDragHandle: true,
      backgroundColor: const Color(0xFFF8F8FB),
      builder: (sheetContext) => SafeArea(
        child: ListView(
          shrinkWrap: true,
          children: [
            const _SheetHeader('Urdu Typography', 'Jameel Noori Nastaleeq is the default'),
            ...fonts.map((font) => _fontTile(font.$1, font.$3, font.$2, element.fontFamily)),
          ],
        ),
      ),
    );
    if (family != null) controller.setSelectedFont(family);
  }
'''
w = w[:start] + font_method + w[end:]

# Make the existing font tile understand the canonical Jameel family name.
w = w.replace("final active = current == family || (current == 'JameelNoori' && family == 'Gulzar');", "final active = current == family;")

W.write_text(w, encoding='utf-8')
print('Premium Jameel-first text composer applied.')
