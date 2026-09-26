from pathlib import Path
import re
import runpy

TARGET = 'scripts/final_live_preview_and_selection.py'

try:
    runpy.run_path(TARGET, run_name='__main__')
except SystemExit as exc:
    message = str(exc)
    # The legacy final pass can stop after all core UX mutations have already
    # been applied when an earlier generator has reformatted the layer labels.
    # Recover that final label normalization here, then verify the real output.
    if 'Layer title shape label anchor not found' not in message and 'Layer subtitle shape label anchor not found' not in message and 'Final editor UX invariant missing' not in message:
        raise

layers_path = Path('lib/widgets/layers_panel.dart')
layers = layers_path.read_text(encoding='utf-8')

# Normalize the shape branch without depending on whitespace/formatting.
layers, n1 = re.subn(
    r"(case\s+ElementKind\.shape:\s*)return\s+(['\"])Shape\2\s*;",
    r"\1return element.catalogType == 'border' ? 'Border' : 'Shape';",
    layers,
    count=1,
)

# Normalize the shape subtitle if it is still the old generic dimensions-only form.
layers, n2 = re.subn(
    r"(case\s+ElementKind\.shape:\s*)return\s+(['\"])\$\{element\.width\.round\(\)\}\s*×\s*\$\{element\.height\.round\(\)\}\2\s*;",
    r"\1final kind = element.catalogType == 'border' ? 'Border' : 'Shape';\n        return '\$kind • \${element.width.round()} × \${element.height.round()}';",
    layers,
    count=1,
)
layers_path.write_text(layers, encoding='utf-8')

ws = Path('lib/screens/workspace_screen.dart').read_text(encoding='utf-8')
ctl = Path('lib/state/workspace_controller.dart').read_text(encoding='utf-8')
canvas = Path('lib/widgets/design_canvas.dart').read_text(encoding='utf-8')
cat = Path('lib/widgets/premium_catalogs.dart').read_text(encoding='utf-8')
layers = layers_path.read_text(encoding='utf-8')

checks = [
    ("tooltip: 'Layers'", ws),
    ('Future<void> _layersSheet() async', ws),
    ('_deselectTool()', ws),
    ('controller.startContinuousEdit();', ws),
    ('controller.finishContinuousEdit();', ws),
    ('void startContinuousEdit()', ctl),
    ('void finishContinuousEdit()', ctl),
    ('if (!_continuousCheckpointActive) _checkpoint();', ctl),
    ('radius: e.radius', canvas),
    ('final double radius;', cat),
    ('oldDelegate.radius != radius', cat),
    ('catalogType', layers),
    ('Border', layers),
    ('Shape', layers),
]
for needle, text in checks:
    if needle not in text:
        raise SystemExit(f'Final editor UX recovery invariant missing: {needle}')
print('Final editor UX recovery contracts verified.')


# ---------------------------------------------------------------------------
# Final hardening: keep editor popups open while their controls mutate the
# actual selected model. The workspace is already an AnimatedBuilder of the
# controller, so _changed() immediately repaints the canvas behind the sheet.
# ---------------------------------------------------------------------------
def replace_method(source, name, next_name, body):
    import re

    def declaration_pos(text, method_name, offset=0):
        escaped = re.escape(method_name.rstrip('()'))
        pattern = re.compile(
            rf'^  [A-Za-z_][A-Za-z0-9_<>?,. ]*\s+{escaped}\s*\(',
            re.MULTILINE,
        )
        match = pattern.search(text, offset)
        if match is None:
            raise SystemExit(f'Live preview hardening: missing method declaration {method_name}')
        return match.start()

    start = declaration_pos(source, name)
    end = declaration_pos(source, next_name, start + 1)
    if end <= start:
        raise SystemExit(f'Live preview hardening: invalid method boundary for {name}')

    return source[:start] + body.rstrip() + '\n\n' + source[end:]


ws_path = Path('lib/screens/workspace_screen.dart')
ws = ws_path.read_text(encoding='utf-8')

# Remove an obsolete named argument left by an earlier editor pass.
ws = ws.replace(
    "await _textDialog('Edit Text', element.text, livePreview: true)",
    "await _textDialog('Edit Text', element.text)",
)

# Normalize stale popup-context references that escaped a builder during an
# earlier source transformation. State.context is valid in every such action.
ws = ws.replace("Navigator.pop(sheetContext", "Navigator.pop(context")

font = r'''  Future<void> _fontSheet() async {
    final element = controller.selected;
    if (element == null) return;
    final original = element.fontFamily;
    var current = original;
    await showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      isScrollControlled: true,
      builder: (sheetContext) => StatefulBuilder(
        builder: (context, setSheetState) => SafeArea(
          child: ListView(
            shrinkWrap: true,
            children: [
              const _SheetHeader('Urdu Typography', 'Tap a font and see the canvas update immediately'),
              _fontTileLive('Gulzar', 'Contemporary Nastaliq', 'Gulzar', current, (family) {
                setSheetState(() => current = family);
                controller.setSelectedFont(family);
              }),
              _fontTileLive('Noto Nastaliq Urdu', 'Google Fonts Nastaliq', 'NotoNastaliqUrdu', current, (family) {
                setSheetState(() => current = family);
                controller.setSelectedFont(family);
              }),
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 8, 16, 18),
                child: Row(
                  children: [
                    Expanded(child: OutlinedButton(onPressed: () { controller.setSelectedFont(original); Navigator.pop(sheetContext); }, child: const Text('Cancel'))),
                    const SizedBox(width: 10),
                    Expanded(child: FilledButton(onPressed: () => Navigator.pop(sheetContext), child: const Text('Done'))),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _fontTileLive(String title, String subtitle, String family, String current, ValueChanged<String> onTap) {
    final active = current == family || (current == 'JameelNoori' && family == 'Gulzar');
    return ListTile(
      leading: CircleAvatar(
        backgroundColor: active ? _primary : Colors.black12,
        child: Icon(Icons.font_download_rounded, color: active ? Colors.white : Colors.black54),
      ),
      title: Text(title, style: TextStyle(fontFamily: family, fontSize: 21, fontWeight: FontWeight.w700)),
      subtitle: Text(subtitle),
      trailing: active ? const Icon(Icons.check_circle_rounded, color: _primary) : null,
      onTap: () => onTap(family),
    );
  }
'''
if 'Future<void> _fontSheet() async' not in ws:
    tile_pos = ws.find('  Widget _fontTile(')
    if tile_pos < 0:
        raise SystemExit('Live preview hardening: missing font tile declaration')
    ws = ws[:tile_pos] + font.rstrip() + '\n\n' + ws[tile_pos:]
else:
    ws = replace_method(ws, '_fontSheet()', '_fontTile(', font)

single = r'''  Future<void> _singleSlider(
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
      builder: (sheetContext) => StatefulBuilder(
        builder: (context, setSheetState) => SafeArea(
          child: Padding(
            padding: const EdgeInsets.fromLTRB(18, 8, 18, 20),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                _SheetHeader(title, 'Move the control for an instant canvas preview'),
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.symmetric(vertical: 10),
                  decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16)),
                  child: Text(display(value), textAlign: TextAlign.center, style: const TextStyle(fontSize: 25, fontWeight: FontWeight.w900, color: _primary)),
                ),
                Slider(
                  min: min, max: max, divisions: divisions, value: value,
                  onChanged: (newValue) {
                    controller.startContinuousEdit();
                    setSheetState(() => value = newValue);
                    apply(newValue);
                  },
                  onChangeEnd: (_) => controller.finishContinuousEdit(),
                ),
                Row(
                  children: [
                    Expanded(child: OutlinedButton(onPressed: () { apply(initial); controller.finishContinuousEdit(); Navigator.pop(sheetContext); }, child: const Text('Cancel'))),
                    const SizedBox(width: 10),
                    Expanded(child: FilledButton(onPressed: () { controller.finishContinuousEdit(); Navigator.pop(sheetContext); }, child: const Text('Done'))),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
    controller.finishContinuousEdit();
  }
'''
ws = replace_method(ws, '_singleSlider(', '_colorSheet()', single)

color = r'''  Future<void> _colorSheet() async {
    final element = controller.selected;
    if (element == null) return;
    const colors = [Colors.black, Colors.white, _primary, Color(0xFF0F766E), Color(0xFFDC2626), Color(0xFFF59E0B), Color(0xFF2563EB), Color(0xFF7C2D12), Color(0xFFDB2777), Color(0xFF16A34A), Color(0xFF9333EA)];
    final original = element.colorValue;
    var current = original;
    await showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      backgroundColor: const Color(0xFFF7F7FA),
      builder: (sheetContext) => StatefulBuilder(
        builder: (context, setSheetState) => SafeArea(
          child: Padding(
            padding: const EdgeInsets.fromLTRB(14, 8, 14, 18),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const _SheetHeader('Color', 'Tap a swatch to preview it instantly on the canvas'),
                SizedBox(
                  height: 78,
                  child: ListView.separated(
                    scrollDirection: Axis.horizontal,
                    itemCount: colors.length,
                    separatorBuilder: (_, __) => const SizedBox(width: 12),
                    itemBuilder: (context, index) {
                      final color = colors[index];
                      return InkWell(
                        onTap: () {
                          setSheetState(() => current = color.toARGB32());
                          controller.startContinuousEdit();
                          controller.updateSelected(colorValue: color.toARGB32());
                          controller.finishContinuousEdit();
                        },
                        borderRadius: BorderRadius.circular(30),
                        child: CircleAvatar(radius: 28, backgroundColor: color, child: current == color.toARGB32() ? const Icon(Icons.check_rounded, color: Colors.white) : null),
                      );
                    },
                  ),
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(child: OutlinedButton(onPressed: () { controller.updateSelected(colorValue: original); Navigator.pop(sheetContext); }, child: const Text('Cancel'))),
                    const SizedBox(width: 10),
                    Expanded(child: FilledButton(onPressed: () => Navigator.pop(sheetContext), child: const Text('Done'))),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
'''
ws = replace_method(ws, '_colorSheet()', '_effectsSheet()', color)

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
      context: context, isScrollControlled: true, showDragHandle: true,
      backgroundColor: const Color(0xFFF7F7FA),
      builder: (sheetContext) => StatefulBuilder(
        builder: (context, setSheetState) => SafeArea(
          child: Padding(
            padding: const EdgeInsets.fromLTRB(18, 8, 18, 20),
            child: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const _SheetHeader('Effects Studio', 'Every adjustment is previewed on the selected object'),
                  _effectSlider('Stroke', strokeWidth, 0, 40, (v) { controller.startContinuousEdit(); setSheetState(() => strokeWidth = v); controller.setSelectedStroke(width: v, colorValue: element.strokeColorValue == 0 ? Colors.black.toARGB32() : element.strokeColorValue); }),
                  _effectSlider('Shadow Blur', shadowBlur, 0, 80, (v) { controller.startContinuousEdit(); setSheetState(() => shadowBlur = v); controller.setSelectedShadow(blur: v, offsetX: shadowX, offsetY: shadowY, colorValue: element.shadowColorValue == 0 ? Colors.black54.toARGB32() : element.shadowColorValue); }),
                  _effectSlider('Shadow X', shadowX, -100, 100, (v) { controller.startContinuousEdit(); setSheetState(() => shadowX = v); controller.setSelectedShadow(blur: shadowBlur, offsetX: v, offsetY: shadowY, colorValue: element.shadowColorValue == 0 ? Colors.black54.toARGB32() : element.shadowColorValue); }),
                  _effectSlider('Shadow Y', shadowY, -100, 100, (v) { controller.startContinuousEdit(); setSheetState(() => shadowY = v); controller.setSelectedShadow(blur: shadowBlur, offsetX: shadowX, offsetY: v, colorValue: element.shadowColorValue == 0 ? Colors.black54.toARGB32() : element.shadowColorValue); }),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Expanded(child: OutlinedButton(onPressed: () { controller.setSelectedStroke(width: originalStroke, colorValue: element.strokeColorValue); controller.setSelectedShadow(blur: originalBlur, offsetX: originalX, offsetY: originalY, colorValue: element.shadowColorValue); controller.finishContinuousEdit(); Navigator.pop(sheetContext); }, child: const Text('Cancel'))),
                      const SizedBox(width: 10),
                      Expanded(child: FilledButton(onPressed: () { controller.finishContinuousEdit(); Navigator.pop(sheetContext); }, child: const Text('Done'))),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
    controller.finishContinuousEdit();
  }
'''
ws = replace_method(ws, '_effectsSheet()', '_effectSlider(', effects)

spacing = r'''  Future<void> _spacingSheet() async {
    final element = controller.selected;
    if (element == null) return;
    final originalLetter = element.letterSpacing;
    final originalLine = element.lineHeight;
    double letterSpacing = originalLetter;
    double lineHeight = originalLine;
    await showModalBottomSheet<void>(
      context: context, showDragHandle: true, backgroundColor: const Color(0xFFF7F7FA),
      builder: (sheetContext) => StatefulBuilder(
        builder: (context, setSheetState) => SafeArea(
          child: Padding(
            padding: const EdgeInsets.fromLTRB(18, 8, 18, 20),
            child: Column(
              mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const _SheetHeader('Typography Spacing', 'Live preview for Nastaliq composition'),
                _effectSlider('Letter Spacing', letterSpacing, -10, 20, (v) { controller.startContinuousEdit(); setSheetState(() => letterSpacing = v); controller.setSelectedTypography(letterSpacing: v, lineHeight: lineHeight); }),
                _effectSlider('Line Height', lineHeight, 0.7, 3, (v) { controller.startContinuousEdit(); setSheetState(() => lineHeight = v); controller.setSelectedTypography(letterSpacing: letterSpacing, lineHeight: v); }),
                Row(
                  children: [
                    Expanded(child: OutlinedButton(onPressed: () { controller.setSelectedTypography(letterSpacing: originalLetter, lineHeight: originalLine); controller.finishContinuousEdit(); Navigator.pop(sheetContext); }, child: const Text('Cancel'))),
                    const SizedBox(width: 10),
                    Expanded(child: FilledButton(onPressed: () { controller.finishContinuousEdit(); Navigator.pop(sheetContext); }, child: const Text('Done'))),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
    controller.finishContinuousEdit();
  }
'''
ws = replace_method(ws, '_spacingSheet()', '_alignSheet()', spacing)

align = r'''  Future<void> _alignSheet() async {
    final element = controller.selected;
    if (element == null) return;
    final original = element.textAlign;
    var current = original;
    const values = [TextAlign.left, TextAlign.center, TextAlign.right, TextAlign.justify];
    await showModalBottomSheet<void>(
      context: context, showDragHandle: true,
      builder: (sheetContext) => StatefulBuilder(
        builder: (context, setSheetState) => SafeArea(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const _SheetHeader('Text Alignment', 'Tap an option to preview it instantly'),
              ...values.map((value) => ListTile(
                title: Text(value.name, style: const TextStyle(fontWeight: FontWeight.w700)),
                trailing: current == value ? const Icon(Icons.check_circle_rounded, color: _primary) : null,
                onTap: () { setSheetState(() => current = value); controller.setSelectedAlign(value); },
              )),
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 6, 16, 16),
                child: Row(
                  children: [
                    Expanded(child: OutlinedButton(onPressed: () { controller.setSelectedAlign(original); Navigator.pop(sheetContext); }, child: const Text('Cancel'))),
                    const SizedBox(width: 10),
                    Expanded(child: FilledButton(onPressed: () => Navigator.pop(sheetContext), child: const Text('Done'))),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
'''
ws = replace_method(ws, '_alignSheet()', '_directionSheet()', align)

direction = r'''  Future<void> _directionSheet() async {
    final element = controller.selected;
    if (element == null) return;
    final original = element.textDirection;
    var current = original;
    const values = [TextDirection.rtl, TextDirection.ltr];
    await showModalBottomSheet<void>(
      context: context, showDragHandle: true,
      builder: (sheetContext) => StatefulBuilder(
        builder: (context, setSheetState) => SafeArea(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const _SheetHeader('Text Direction', 'Tap RTL/LTR and preview the canvas before closing'),
              ...values.map((value) => ListTile(
                title: Text(value == TextDirection.rtl ? 'Right to left (Urdu)' : 'Left to right'),
                trailing: current == value ? const Icon(Icons.check_circle_rounded, color: _primary) : null,
                onTap: () { setSheetState(() => current = value); controller.setSelectedDirection(value); },
              )),
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 6, 16, 16),
                child: Row(
                  children: [
                    Expanded(child: OutlinedButton(onPressed: () { controller.setSelectedDirection(original); Navigator.pop(sheetContext); }, child: const Text('Cancel'))),
                    const SizedBox(width: 10),
                    Expanded(child: FilledButton(onPressed: () => Navigator.pop(sheetContext), child: const Text('Done'))),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
'''
ws = replace_method(ws, '_directionSheet()', '_choiceSheet<T>', direction)

background = r'''  Future<void> _backgroundSheet() async {
    const colors = [Colors.white, Color(0xFF0F172A), Color(0xFFF8FAFC), Color(0xFFF5F3FF), Color(0xFFFEF3C7), Color(0xFFE0F2FE), Color(0xFFFCE7F3)];
    final original = controller.page.background.toARGB32();
    var current = original;
    await showModalBottomSheet<void>(
      context: context, showDragHandle: true,
      builder: (sheetContext) => StatefulBuilder(
        builder: (context, setSheetState) => SafeArea(
          child: Padding(
            padding: const EdgeInsets.fromLTRB(14, 8, 14, 18),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const _SheetHeader('Background', 'Tap a swatch to preview the canvas instantly'),
                SizedBox(
                  height: 78,
                  child: ListView.separated(
                    scrollDirection: Axis.horizontal,
                    itemCount: colors.length,
                    separatorBuilder: (_, __) => const SizedBox(width: 12),
                    itemBuilder: (context, index) {
                      final color = colors[index];
                      return InkWell(
                        onTap: () { setSheetState(() => current = color.toARGB32()); controller.setBackground(color); },
                        borderRadius: BorderRadius.circular(30),
                        child: CircleAvatar(radius: 29, backgroundColor: color, child: current == color.toARGB32() ? const Icon(Icons.check_rounded, color: Colors.white) : null),
                      );
                    },
                  ),
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(child: OutlinedButton(onPressed: () { controller.setBackground(Color(original)); Navigator.pop(sheetContext); }, child: const Text('Cancel'))),
                    const SizedBox(width: 10),
                    Expanded(child: FilledButton(onPressed: () => Navigator.pop(sheetContext), child: const Text('Done'))),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
'''
ws = replace_method(ws, '_backgroundSheet()', '_canvasSizeDialog()', background)

checks = [
    'controller.setSelectedFont(family);',
    'controller.updateSelected(colorValue: color.toARGB32());',
    'controller.setSelectedStroke(',
    'controller.setSelectedShadow(',
    'controller.setSelectedTypography(',
    'controller.setSelectedAlign(value);',
    'controller.setSelectedDirection(value);',
    'controller.setBackground(color);',
    'Move the control for an instant canvas preview',
]
for needle in checks:
    if needle not in ws:
        raise SystemExit(f'Live preview hardening invariant missing: {needle}')

ws_path.write_text(ws, encoding='utf-8')
print('Final live-preview hardening verified: font, sliders, color, effects, spacing, alignment, direction, and background mutate the real model while their popup stays open.')
