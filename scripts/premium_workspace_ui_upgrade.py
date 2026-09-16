from pathlib import Path
import re

W = Path('lib/screens/workspace_screen.dart')
w = W.read_text(encoding='utf-8')

# Keep editing controls at the bottom of the screen: no centered AlertDialog for editor actions.
w = w.replace('Future<String?> _textDialog(String title, String initial) async {', 'Future<String?> _textDialog(String title, String initial) async {', 1)

start = w.index('  Future<String?> _textDialog(')
end = w.index('\n  Future<void> _fontSheet()', start)
text_method = r'''  Future<String?> _textDialog(String title, String initial) async {
    final textController = TextEditingController(text: initial);
    final isEditing = controller.selected?.kind == ElementKind.text && initial == controller.selected?.text;
    var preview = initial;
    final result = await showModalBottomSheet<String>(
      context: context,
      isScrollControlled: true,
      showDragHandle: true,
      backgroundColor: const Color(0xFFF7F7FA),
      builder: (sheetContext) {
        return StatefulBuilder(
          builder: (context, setSheetState) {
            final bottom = MediaQuery.viewInsetsOf(context).bottom;
            return SafeArea(
              child: Padding(
                padding: EdgeInsets.fromLTRB(16, 8, 16, 16 + bottom),
                child: SingleChildScrollView(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      _SheetHeader(title, 'Type in Urdu and see the result before applying'),
                      Container(
                        constraints: const BoxConstraints(minHeight: 92, maxHeight: 180),
                        margin: const EdgeInsets.only(bottom: 12),
                        padding: const EdgeInsets.all(14),
                        decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(18), border: Border.all(color: _primary.withValues(alpha: .18))),
                        alignment: Alignment.center,
                        child: Directionality(
                          textDirection: TextDirection.rtl,
                          child: Text(preview.isEmpty ? 'لائیو پری ویو' : preview, textAlign: TextAlign.center, style: const TextStyle(fontFamily: 'Gulzar', fontSize: 25, height: 1.35)),
                        ),
                      ),
                      TextField(
                        controller: textController,
                        autofocus: true,
                        maxLines: 5,
                        textDirection: TextDirection.rtl,
                        style: const TextStyle(fontFamily: 'Gulzar', fontSize: 21),
                        onChanged: (value) {
                          setSheetState(() => preview = value);
                          if (isEditing && controller.selected != null) controller.editSelectedText(value);
                        },
                        decoration: InputDecoration(hintText: 'اردو متن', border: OutlineInputBorder(borderRadius: BorderRadius.circular(16))),
                      ),
                      const SizedBox(height: 12),
                      Row(
                        children: [
                          Expanded(child: OutlinedButton(onPressed: () { if (isEditing) controller.editSelectedText(initial); Navigator.pop(sheetContext); }, child: const Text('Cancel'))),
                          const SizedBox(width: 10),
                          Expanded(child: FilledButton.icon(onPressed: () => Navigator.pop(sheetContext, textController.text), icon: const Icon(Icons.check_rounded), label: const Text('Apply'))),
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
    textController.dispose();
    return result;
  }
'''
w = w[:start] + text_method + w[end:]

# Slider sheets now update the actual selection continuously. Cancel restores the original value.
start = w.index('  Future<void> _singleSlider(')
end = w.index('\n  Future<void> _colorSheet()', start)
slider_method = r'''  Future<void> _singleSlider(
    String title,
    double initial,
    double min,
    double max,
    String Function(double) display,
    ValueChanged<double> apply, {
    int? divisions,
  }) async {
    double value = initial.clamp(min, max).toDouble();
    await showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      backgroundColor: const Color(0xFFF7F7FA),
      builder: (sheetContext) {
        return StatefulBuilder(
          builder: (context, setSheetState) {
            return SafeArea(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(18, 8, 18, 20),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    _SheetHeader(title, 'Move the slider for an instant canvas preview'),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.symmetric(vertical: 10),
                      decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16)),
                      child: Text(display(value), textAlign: TextAlign.center, style: const TextStyle(fontSize: 25, fontWeight: FontWeight.w900, color: _primary)),
                    ),
                    Slider(min: min, max: max, divisions: divisions, value: value, onChanged: (newValue) { setSheetState(() => value = newValue); apply(newValue); }),
                    Row(children: [Expanded(child: OutlinedButton(onPressed: () { apply(initial); Navigator.pop(sheetContext); }, child: const Text('Cancel'))), const SizedBox(width: 10), Expanded(child: FilledButton(onPressed: () => Navigator.pop(sheetContext), child: const Text('Done')))]),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }
'''
w = w[:start] + slider_method + w[end:]

# Effects and spacing: live-update each value and restore on cancel.
start = w.index('  Future<void> _effectsSheet()')
end = w.index('\n  Widget _effectSlider', start)
effects = r'''  Future<void> _effectsSheet() async {
    final element = controller.selected;
    if (element == null) return;
    final originalStroke = element.strokeWidth;
    final originalBlur = element.shadowBlur;
    final originalX = element.shadowOffsetX;
    final originalY = element.shadowOffsetY;
    double strokeWidth = originalStroke;
    double shadowBlur = originalBlur;
    double shadowX = originalX;
    double shadowY = originalY;

    await showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      showDragHandle: true,
      backgroundColor: const Color(0xFFF7F7FA),
      builder: (sheetContext) => StatefulBuilder(builder: (context, setSheetState) {
        void preview() => controller.setSelectedStroke(width: strokeWidth, colorValue: element.strokeColorValue == 0 ? Colors.black.toARGB32() : element.strokeColorValue);
        void previewShadow() => controller.setSelectedShadow(blur: shadowBlur, offsetX: shadowX, offsetY: shadowY, colorValue: element.shadowColorValue == 0 ? Colors.black54.toARGB32() : element.shadowColorValue);
        return SafeArea(child: Padding(padding: const EdgeInsets.fromLTRB(18, 8, 18, 20), child: SingleChildScrollView(child: Column(mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.start, children: [
          const _SheetHeader('Effects Studio', 'Every adjustment is previewed on the selected object'),
          _effectSlider('Stroke', strokeWidth, 0, 40, (v) { setSheetState(() => strokeWidth = v); preview(); }),
          _effectSlider('Shadow Blur', shadowBlur, 0, 80, (v) { setSheetState(() => shadowBlur = v); previewShadow(); }),
          _effectSlider('Shadow X', shadowX, -100, 100, (v) { setSheetState(() => shadowX = v); previewShadow(); }),
          _effectSlider('Shadow Y', shadowY, -100, 100, (v) { setSheetState(() => shadowY = v); previewShadow(); }),
          Row(children: [Expanded(child: OutlinedButton(onPressed: () { controller.setSelectedStroke(width: originalStroke, colorValue: element.strokeColorValue); controller.setSelectedShadow(blur: originalBlur, offsetX: originalX, offsetY: originalY, colorValue: element.shadowColorValue); Navigator.pop(sheetContext); }, child: const Text('Cancel'))), const SizedBox(width: 10), Expanded(child: FilledButton(onPressed: () => Navigator.pop(sheetContext), child: const Text('Done')))]),
        ]))));
      }),
    );
  }
'''
w = w[:start] + effects + w[end:]

start = w.index('  Future<void> _spacingSheet()')
end = w.index('\n  Future<void> _alignSheet()', start)
spacing = r'''  Future<void> _spacingSheet() async {
    final element = controller.selected;
    if (element == null) return;
    final originalLetter = element.letterSpacing;
    final originalLine = element.lineHeight;
    double letterSpacing = originalLetter;
    double lineHeight = originalLine;
    await showModalBottomSheet<void>(context: context, showDragHandle: true, backgroundColor: const Color(0xFFF7F7FA), builder: (sheetContext) => StatefulBuilder(builder: (context, setSheetState) {
      return SafeArea(child: Padding(padding: const EdgeInsets.fromLTRB(18, 8, 18, 20), child: Column(mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.start, children: [
        const _SheetHeader('Typography Spacing', 'Live preview for Nastaliq composition'),
        _effectSlider('Letter Spacing', letterSpacing, -10, 20, (v) { setSheetState(() => letterSpacing = v); controller.setSelectedTypography(letterSpacing: v, lineHeight: lineHeight); }),
        _effectSlider('Line Height', lineHeight, 0.7, 3, (v) { setSheetState(() => lineHeight = v); controller.setSelectedTypography(letterSpacing: letterSpacing, lineHeight: v); }),
        Row(children: [Expanded(child: OutlinedButton(onPressed: () { controller.setSelectedTypography(letterSpacing: originalLetter, lineHeight: originalLine); Navigator.pop(sheetContext); }, child: const Text('Cancel'))), const SizedBox(width: 10), Expanded(child: FilledButton(onPressed: () => Navigator.pop(sheetContext), child: const Text('Done')))]),
      ])));
    }));
  }
'''
w = w[:start] + spacing + w[end:]

# Background and color controls become compact horizontal palettes with immediate preview.
start = w.index('  Future<void> _backgroundSheet()')
end = w.index('\n  Future<void> _canvasSizeDialog()', start)
background = r'''  Future<void> _backgroundSheet() async {
    const colors = [Colors.white, Color(0xFF0F172A), Color(0xFFF8FAFC), Color(0xFFF5F3FF), Color(0xFFFEF3C7), Color(0xFFE0F2FE), Color(0xFFFCE7F3)];
    final original = controller.project.backgroundColorValue;
    await showModalBottomSheet<void>(context: context, showDragHandle: true, backgroundColor: const Color(0xFFF7F7FA), builder: (sheetContext) => SafeArea(child: Padding(padding: const EdgeInsets.fromLTRB(14, 8, 14, 18), child: Column(mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.start, children: [
      const _SheetHeader('Background', 'Tap a swatch to preview it instantly'),
      SizedBox(height: 78, child: ListView.separated(scrollDirection: Axis.horizontal, itemCount: colors.length, separatorBuilder: (_, __) => const SizedBox(width: 12), itemBuilder: (context, index) => InkWell(onTap: () => controller.setBackground(colors[index]), borderRadius: BorderRadius.circular(30), child: CircleAvatar(radius: 29, backgroundColor: colors[index], child: colors[index].toARGB32() == controller.project.backgroundColorValue ? const Icon(Icons.check_rounded, color: Colors.white) : null)))),
      const SizedBox(height: 12),
      Row(children: [Expanded(child: OutlinedButton(onPressed: () { controller.setBackground(Color(original)); Navigator.pop(sheetContext); }, child: const Text('Cancel'))), const SizedBox(width: 10), Expanded(child: FilledButton(onPressed: () => Navigator.pop(sheetContext), child: const Text('Done')))]),
    ]))));
  }
'''
w = w[:start] + background + w[end:]

# Make object color a horizontally scrollable, instant-preview palette.
start = w.index('  Future<void> _colorSheet()')
end = w.index('\n  Future<void> _effectsSheet()', start)
color = r'''  Future<void> _colorSheet() async {
    final element = controller.selected;
    if (element == null) return;
    const colors = [Colors.black, Colors.white, _primary, Color(0xFF0F766E), Color(0xFFDC2626), Color(0xFFF59E0B), Color(0xFF2563EB), Color(0xFF7C2D12), Color(0xFFDB2777), Color(0xFF16A34A), Color(0xFF9333EA)];
    final original = element.colorValue;
    await showModalBottomSheet<void>(context: context, showDragHandle: true, backgroundColor: const Color(0xFFF7F7FA), builder: (sheetContext) => SafeArea(child: Padding(padding: const EdgeInsets.fromLTRB(14, 8, 14, 18), child: Column(mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.start, children: [
      const _SheetHeader('Color', 'Horizontal palette • live canvas preview'),
      SizedBox(height: 76, child: ListView.separated(scrollDirection: Axis.horizontal, itemCount: colors.length, separatorBuilder: (_, __) => const SizedBox(width: 12), itemBuilder: (context, index) { final color = colors[index]; return InkWell(onTap: () => controller.updateSelected(colorValue: color.toARGB32()), borderRadius: BorderRadius.circular(30), child: CircleAvatar(radius: 28, backgroundColor: color, child: color.toARGB32() == controller.selected?.colorValue ? const Icon(Icons.check_rounded, color: Colors.white) : null)); })),
      const SizedBox(height: 12),
      Row(children: [Expanded(child: OutlinedButton(onPressed: () { controller.updateSelected(colorValue: original); Navigator.pop(sheetContext); }, child: const Text('Cancel'))), const SizedBox(width: 10), Expanded(child: FilledButton(onPressed: () => Navigator.pop(sheetContext), child: const Text('Done')))]),
    ]))));
  }
'''
w = w[:start] + color + w[end:]

# Convert canvas size to a bottom sheet with a live visual dimension preview.
start = w.index('  Future<void> _canvasSizeDialog()')
end = w.index('\n  Future<void> _pickImage()', start)
canvas = r'''  Future<void> _canvasSizeDialog() async {
    final widthController = TextEditingController(text: controller.page.size.width.round().toString());
    final heightController = TextEditingController(text: controller.page.size.height.round().toString());
    var width = controller.page.size.width;
    var height = controller.page.size.height;
    final originalWidth = width;
    final originalHeight = height;
    final accepted = await showModalBottomSheet<bool>(context: context, isScrollControlled: true, showDragHandle: true, backgroundColor: const Color(0xFFF7F7FA), builder: (sheetContext) => StatefulBuilder(builder: (context, setSheetState) {
      void refresh() => setSheetState(() { width = (double.tryParse(widthController.text) ?? originalWidth).clamp(64, 16000).toDouble(); height = (double.tryParse(heightController.text) ?? originalHeight).clamp(64, 16000).toDouble(); });
      return SafeArea(child: Padding(padding: EdgeInsets.fromLTRB(18, 8, 18, 18 + MediaQuery.viewInsetsOf(context).bottom), child: SingleChildScrollView(child: Column(mainAxisSize: MainAxisSize.min, children: [
        const _SheetHeader('Canvas Size', 'Live dimension preview before resizing'),
        Container(height: 120, width: double.infinity, alignment: Alignment.center, decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(18)), child: FittedBox(child: Container(width: width, height: height, decoration: BoxDecoration(color: const Color(0xFFF5F3FF), border: Border.all(color: _primary, width: 2), borderRadius: BorderRadius.circular(6)), child: Center(child: Text('${width.round()} × ${height.round()}', style: const TextStyle(fontWeight: FontWeight.w900))))),
        const SizedBox(height: 14),
        Row(children: [Expanded(child: TextField(controller: widthController, keyboardType: TextInputType.number, onChanged: (_) => refresh(), decoration: const InputDecoration(labelText: 'Width', border: OutlineInputBorder()))), const SizedBox(width: 12), Expanded(child: TextField(controller: heightController, keyboardType: TextInputType.number, onChanged: (_) => refresh(), decoration: const InputDecoration(labelText: 'Height', border: OutlineInputBorder()))]),
        const SizedBox(height: 12),
        Row(children: [Expanded(child: OutlinedButton(onPressed: () => Navigator.pop(sheetContext, false), child: const Text('Cancel'))), const SizedBox(width: 10), Expanded(child: FilledButton(onPressed: () => Navigator.pop(sheetContext, true), child: const Text('Resize')))]),
      ]))));
    }));
    if (accepted == true) controller.resizeCanvas(width, height);
    widthController.dispose();
    heightController.dispose();
  }
'''
w = w[:start] + canvas + w[end:]

# Make choice panels preview their selected state instead of looking like generic dialogs.
start = w.index('  Future<T?> _choiceSheet<T>')
end = w.index('\n  Future<void> _arrangeSheet()', start)
choice = r'''  Future<T?> _choiceSheet<T>(String title, List<T> values, String Function(T) label) {
    return showModalBottomSheet<T>(context: context, showDragHandle: true, backgroundColor: const Color(0xFFF7F7FA), builder: (sheetContext) => SafeArea(child: Padding(padding: const EdgeInsets.fromLTRB(14, 8, 14, 18), child: Column(mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.start, children: [
      _SheetHeader(title, 'Tap an option to preview and apply'),
      SizedBox(height: 76, child: ListView.separated(scrollDirection: Axis.horizontal, itemCount: values.length, separatorBuilder: (_, __) => const SizedBox(width: 8), itemBuilder: (context, index) => FilledButton.tonal(onPressed: () => Navigator.pop(sheetContext, values[index]), child: Text(label(values[index]))))),
    ]))));
  }
'''
w = w[:start] + choice + w[end:]

# Ensure bottom-sheet content can never grow past the usable viewport.
w = w.replace("return SafeArea(\n          child: Wrap(", "return SafeArea(\n          child: SingleChildScrollView(child: Wrap(", 2)
# Close the two inserted SingleChildScrollViews only where the original Wrap was directly closed.
w = w.replace("            ],\n          ),\n        );\n      },\n    );\n  }\n\n  Future<void> _moreSheet", "            ],\n          )),\n        );\n      },\n    );\n  }\n\n  Future<void> _moreSheet", 1)
w = w.replace("            ],\n          ),\n        );\n      },\n    );\n  }\n\n  Future<void> _pagesSheet", "            ],\n          )),\n        );\n      },\n    );\n  }\n\n  Future<void> _pagesSheet", 1)

W.write_text(w, encoding='utf-8')
print('Premium workspace UI upgrade applied.')
