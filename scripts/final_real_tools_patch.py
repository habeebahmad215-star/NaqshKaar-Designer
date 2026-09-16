from pathlib import Path

W = Path('lib/screens/workspace_screen.dart')
C = Path('lib/state/workspace_controller.dart')


def replace_method(source, signature, replacement):
    start = source.index(signature)
    brace = source.index('{', start)
    depth = 0
    for i in range(brace, len(source)):
        if source[i] == '{': depth += 1
        elif source[i] == '}':
            depth -= 1
            if depth == 0: return source[:start] + replacement.rstrip() + source[i+1:]
    raise SystemExit(signature)

w = W.read_text(encoding='utf-8')
w = replace_method(w, '  Future<void> _colorSheet()', r'''  Future<void> _colorSheet() async {
    final element = controller.selected;
    if (element == null) return;
    var color = Color(element.colorValue);
    var hsv = HSVColor.fromColor(color);
    final hex = TextEditingController(text: color.toARGB32().toRadixString(16).padLeft(8, '0').substring(2).toUpperCase());
    await showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      showDragHandle: true,
      builder: (sheetContext) => StatefulBuilder(builder: (_, setSheetState) {
        void applyHsv() { color = hsv.toColor(); setSheetState(() {}); }
        return SafeArea(child: Padding(padding: EdgeInsets.fromLTRB(18, 8, 18, MediaQuery.viewInsetsOf(sheetContext).bottom + 22), child: SingleChildScrollView(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const _SheetHeader('Color Studio', 'Full palette, custom HEX and precise HSV control'),
          Row(children: [Container(width: 58, height: 58, decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(16), border: Border.all(color: Colors.black12))), const SizedBox(width: 12), Expanded(child: Text('#${color.toARGB32().toRadixString(16).padLeft(8, '0').substring(2).toUpperCase()}', style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w900)))]),
          const SizedBox(height: 12),
          TextField(controller: hex, textCapitalization: TextCapitalization.characters, decoration: const InputDecoration(labelText: 'HEX color', prefixText: '#', border: OutlineInputBorder()), onSubmitted: (v) { final value = int.tryParse(v.replaceFirst('#', ''), radix: 16); if (value != null && v.length >= 6) { color = Color(0xFF000000 | (value & 0xFFFFFF)); hsv = HSVColor.fromColor(color); setSheetState(() {}); } }),
          const SizedBox(height: 12),
          const Text('Hue', style: TextStyle(fontWeight: FontWeight.w800)), Slider(min: 0, max: 360, value: hsv.hue, onChanged: (v) { hsv = hsv.withHue(v); applyHsv(); }),
          const Text('Saturation', style: TextStyle(fontWeight: FontWeight.w800)), Slider(value: hsv.saturation, onChanged: (v) { hsv = hsv.withSaturation(v); applyHsv(); }),
          const Text('Brightness', style: TextStyle(fontWeight: FontWeight.w800)), Slider(value: hsv.value, onChanged: (v) { hsv = hsv.withValue(v); applyHsv(); }),
          const Text('Opacity', style: TextStyle(fontWeight: FontWeight.w800)), Slider(value: hsv.alpha, onChanged: (v) { hsv = hsv.withAlpha(v); applyHsv(); }),
          const SizedBox(height: 8),
          Wrap(spacing: 8, runSpacing: 8, children: [for (final c in const [Colors.black, Colors.white, Colors.red, Colors.orange, Colors.amber, Colors.green, Colors.teal, Colors.cyan, Colors.blue, Colors.indigo, Colors.purple, Colors.pink, Color(0xFFD4AF37), Color(0xFF8B5E34), Color(0xFF0F172A), Color(0xFFE2E8F0), Color(0xFFF1F5F9), Color(0xFF7C3AED), Color(0xFF059669), Color(0xFFDC2626)]) InkWell(onTap: () { color = c; hsv = HSVColor.fromColor(c); hex.text = c.toARGB32().toRadixString(16).padLeft(8, '0').substring(2).toUpperCase(); setSheetState(() {}); }, child: CircleAvatar(radius: 20, backgroundColor: c))]),
          const SizedBox(height: 14),
          SizedBox(width: double.infinity, child: FilledButton.icon(onPressed: () { controller.updateSelected(colorValue: color.toARGB32()); Navigator.pop(sheetContext); }, icon: const Icon(Icons.check_rounded), label: const Text('Apply Color'))),
        ]))));
      }),
    );
    hex.dispose();
  }
''')
if 'case ElementKind.drawing:' not in w.split('String _elementLabel')[1].split('Widget _tool')[0]:
    w = w.replace("      case ElementKind.shape:\n        return 'Shape • ${element.width.round()} × ${element.height.round()}';", "      case ElementKind.shape:\n        return 'Shape • ${element.shapeType} • ${element.width.round()} × ${element.height.round()}';\n      case ElementKind.drawing:\n        return 'Drawing • ${element.drawingPoints.length} points';")
W.write_text(w, encoding='utf-8')

c = C.read_text(encoding='utf-8')
needle = "  DesignElement addImageUrl(String url)"
if 'void addTable(int rows, int cols)' not in c:
    insert = """  void addTable(int rows, int cols) {\n    if (rows < 1 || cols < 1) return;\n    _checkpoint();\n    final cellW = page.size.width / cols;\n    final cellH = (page.size.height * .45 / rows).clamp(32.0, 120.0).toDouble();\n    final totalH = cellH * rows;\n    final top = (page.size.height - totalH) / 2;\n    for (var r = 0; r < rows; r++) {\n      for (var col = 0; col < cols; col++) {\n        page.elements.add(DesignElement(id: _newId('cell'), kind: ElementKind.shape, x: col * cellW, y: top + r * cellH, width: cellW, height: cellH, shapeType: 'rectangle', colorValue: Colors.transparent.toARGB32(), radius: 0, strokeWidth: 1.5, strokeColorValue: Colors.black.toARGB32()));\n      }\n    }\n    selectedId = page.elements.isEmpty ? null : page.elements.last.id;\n    _changed();\n  }\n\n"""
    c = c.replace(needle, insert + needle)
C.write_text(c, encoding='utf-8')

# Replace the table's inline mutation with one undoable controller action.
w = W.read_text(encoding='utf-8')
old = "final cellW = controller.page.size.width / cols; final cellH = 70.0; for (var r = 0; r < rows; r++) { for (var c = 0; c < cols; c++) { final e = controller.addShape(shapeType: 'rectangle'); e.x = c * cellW; e.y = r * cellH; e.width = cellW; e.height = cellH; e.radius = 0; e.colorValue = Colors.transparent.toARGB32(); e.strokeWidth = 2; e.strokeColorValue = Colors.black.toARGB32(); } }"
if old in w:
    w = w.replace(old, 'controller.addTable(rows, cols);')
W.write_text(w, encoding='utf-8')
print('Final real-tools patch applied.')