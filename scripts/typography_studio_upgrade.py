from pathlib import Path

controller = Path('lib/state/workspace_controller.dart')
text = controller.read_text()

if 'applyTypographyPreset' not in text:
    marker = '  void setSelectedTypography({double? letterSpacing, double? lineHeight}) {'
    idx = text.find(marker)
    if idx < 0:
        raise SystemExit('setSelectedTypography not found')
    # Insert before the existing typography setter so the build-time feature has
    # a single controller API for preset application and one undo checkpoint.
    methods = '''  void applyTypographyPreset({required double fontSize, required double letterSpacing, required double lineHeight, required bool bold, required bool italic}) {
    final e = selected;
    if (e == null || e.kind != ElementKind.text || e.locked) return;
    _checkpoint();
    e.fontSize = fontSize.clamp(8, 300).toDouble();
    e.letterSpacing = letterSpacing.clamp(-10, 20).toDouble();
    e.lineHeight = lineHeight.clamp(.7, 3).toDouble();
    e.bold = bold;
    e.italic = italic;
    _changed();
  }

'''
    text = text[:idx] + methods + text[idx:]
    controller.write_text(text)

workspace = Path('lib/screens/workspace_screen.dart')
text = workspace.read_text()
if '_typographyStudioSheet' not in text:
    anchor = "      if (isText) _tool(Icons.format_size_rounded, '${element.fontSize.round()}', () => _fontSize(element)),\n"
    replacement = anchor + "      if (isText) _tool(Icons.text_format_rounded, 'Type', _typographyStudioSheet),\n"
    if anchor not in text:
        raise SystemExit('font size toolbar anchor not found')
    text = text.replace(anchor, replacement, 1)

    marker = '  Future<void> _moreSheet() async {'
    idx = text.find(marker)
    if idx < 0:
        raise SystemExit('_moreSheet not found')
    sheet = r'''  Future<void> _typographyStudioSheet() async {
    final element = controller.selected;
    if (element == null || element.kind != ElementKind.text) return;
    var size = element.fontSize;
    var spacing = element.letterSpacing;
    var lineHeight = element.lineHeight;
    await showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      showDragHandle: true,
      builder: (sheetContext) => StatefulBuilder(
        builder: (context, setSheetState) => SafeArea(
          child: Padding(
            padding: const EdgeInsets.fromLTRB(18, 8, 18, 24),
            child: SingleChildScrollView(
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                const _SheetHeader('Typography Studio', 'Fine control for premium Urdu composition'),
                const SizedBox(height: 8),
                const Text('Presets', style: TextStyle(fontWeight: FontWeight.w900, fontSize: 13)),
                const SizedBox(height: 7),
                Wrap(spacing: 8, runSpacing: 8, children: [
                  _typePreset('Classic', 64, 0, 1.25, false, false),
                  _typePreset('Headline', 86, -1, 1.05, true, false),
                  _typePreset('Elegant', 72, 0.5, 1.35, false, true),
                  _typePreset('Compact', 52, -0.5, 1.05, true, false),
                ]),
                const SizedBox(height: 10),
                _effectSlider('Font Size', size, 8, 300, (v) => setSheetState(() => size = v)),
                _effectSlider('Letter Spacing', spacing, -10, 20, (v) => setSheetState(() => spacing = v)),
                _effectSlider('Line Height', lineHeight, .7, 3, (v) => setSheetState(() => lineHeight = v)),
                const SizedBox(height: 4),
                Row(children: [
                  Expanded(child: OutlinedButton.icon(
                    onPressed: () { controller.toggleSelectedBold(); setSheetState(() {}); },
                    icon: Icon(Icons.format_bold_rounded, color: element.bold ? _primary : null), label: Text(element.bold ? 'Bold On' : 'Bold'),
                  )),
                  const SizedBox(width: 8),
                  Expanded(child: OutlinedButton.icon(
                    onPressed: () { controller.toggleSelectedItalic(); setSheetState(() {}); },
                    icon: Icon(Icons.format_italic_rounded, color: element.italic ? _primary : null), label: Text(element.italic ? 'Italic On' : 'Italic'),
                  )),
                ]),
                const SizedBox(height: 8),
                SizedBox(width: double.infinity, child: FilledButton.icon(
                  onPressed: () { controller.setSelectedFontSize(size); controller.setSelectedTypography(letterSpacing: spacing, lineHeight: lineHeight); Navigator.pop(sheetContext); },
                  icon: const Icon(Icons.check_rounded), label: const Text('Apply typography'),
                )),
              ]),
            ),
          ),
        ),
      ),
    );
  }

  Widget _typePreset(String label, double fontSize, double letterSpacing, double lineHeight, bool bold, bool italic) {
    return OutlinedButton(
      onPressed: () => controller.applyTypographyPreset(fontSize: fontSize, letterSpacing: letterSpacing, lineHeight: lineHeight, bold: bold, italic: italic),
      style: OutlinedButton.styleFrom(padding: const EdgeInsets.symmetric(horizontal: 13, vertical: 10)),
      child: Text(label),
    );
  }

'''
    text = text[:idx] + sheet + text[idx:]
    workspace.write_text(text)

readme = Path('README.md')
r = readme.read_text()
if '- Typography Studio' not in r:
    r = r.replace('- Advanced searchable layer manager\n', '- Advanced searchable layer manager\n- Typography Studio: Urdu presets, size, spacing and line-height controls\n')
    readme.write_text(r)

print('Typography Studio upgrade applied successfully')
