from pathlib import Path

WORKSPACE = Path('lib/screens/workspace_screen.dart')
MODEL = Path('lib/models/design_models.dart')
CONTROLLER = Path('lib/state/workspace_controller.dart')
CANVAS = Path('lib/widgets/design_canvas.dart')


def replace_method(source: str, signature: str, replacement: str) -> str:
    start = source.index(signature)
    brace = source.index('{', start)
    depth = 0
    for i in range(brace, len(source)):
        if source[i] == '{':
            depth += 1
        elif source[i] == '}':
            depth -= 1
            if depth == 0:
                return source[:start] + replacement.rstrip() + source[i + 1:]
    raise SystemExit(f'Could not close method: {signature}')


# Persist stock/network images and richer vector shapes.
model = MODEL.read_text(encoding='utf-8')
model = model.replace('const int kSchemaVersion = 3;', 'const int kSchemaVersion = 4;')
model = model.replace('enum ElementKind { text, shape, image }', 'enum ElementKind { text, shape, image, drawing }')
model = model.replace("  Uint8List? imageBytes;\n  double radius;", "  Uint8List? imageBytes;\n  String? imageUrl;\n  String shapeType;\n  List<Offset> drawingPoints;\n  double radius;")
model = model.replace("    this.imageBytes,\n    this.radius = 18,", "    this.imageBytes,\n    this.imageUrl,\n    this.shapeType = 'rectangle',\n    List<Offset>? drawingPoints,\n    this.radius = 18,\n  }) : drawingPoints = drawingPoints ?? const [];")
model = model.replace("        'textDirection': textDirection == TextDirection.rtl ? 'rtl' : 'ltr',\n        'imageBytes': imageBytes == null ? null : base64Encode(imageBytes!), 'radius': radius,", "        'textDirection': textDirection == TextDirection.rtl ? 'rtl' : 'ltr',\n        'imageBytes': imageBytes == null ? null : base64Encode(imageBytes!),\n        'imageUrl': imageUrl,\n        'shapeType': shapeType,\n        'drawingPoints': drawingPoints.map((p) => {'x': p.dx, 'y': p.dy}).toList(),\n        'radius': radius,")
model = model.replace("    Uint8List? bytes;\n    final raw = json['imageBytes'];", "    Uint8List? bytes;\n    final raw = json['imageBytes'];")
model = model.replace("    final storedFont = json['fontFamily']?.toString();", "    final points = <Offset>[];\n    final rawPoints = json['drawingPoints'];\n    if (rawPoints is List) {\n      for (final item in rawPoints.whereType<Map>()) {\n        final x = (item['x'] as num?)?.toDouble();\n        final y = (item['y'] as num?)?.toDouble();\n        if (x != null && y != null) points.add(Offset(x, y));\n      }\n    }\n    final storedFont = json['fontFamily']?.toString();")
model = model.replace("      imageBytes: bytes, radius: (json['radius'] as num?)?.toDouble() ?? 18,", "      imageBytes: bytes,\n      imageUrl: json['imageUrl']?.toString(),\n      shapeType: json['shapeType']?.toString() ?? 'rectangle',\n      drawingPoints: points,\n      radius: (json['radius'] as num?)?.toDouble() ?? 18,")
MODEL.write_text(model, encoding='utf-8')

# Add controller primitives only once.
controller = CONTROLLER.read_text(encoding='utf-8')
controller = controller.replace(
    "  DesignElement addShape() { _checkpoint(); final e = DesignElement(id: _newId('shape'), kind: ElementKind.shape, x: page.size.width * .35, y: page.size.height * .3, width: 320, height: 220, colorValue: const Color(0xFF7C3AED).toARGB32()); page.elements.add(e); selectedId = e.id; _changed(); return e; }",
    "  DesignElement addShape({String shapeType = 'rectangle'}) { _checkpoint(); final e = DesignElement(id: _newId('shape'), kind: ElementKind.shape, x: page.size.width * .35, y: page.size.height * .3, width: 320, height: 220, shapeType: shapeType, colorValue: const Color(0xFF7C3AED).toARGB32()); page.elements.add(e); selectedId = e.id; _changed(); return e; }\n\n  DesignElement addImageUrl(String url) { _checkpoint(); final e = DesignElement(id: _newId('stock'), kind: ElementKind.image, x: page.size.width * .15, y: page.size.height * .2, width: page.size.width * .7, height: page.size.height * .45, imageUrl: url); page.elements.add(e); selectedId = e.id; _changed(); return e; }\n\n  DesignElement addDrawing(List<Offset> points) { _checkpoint(); final e = DesignElement(id: _newId('drawing'), kind: ElementKind.drawing, x: 0, y: 0, width: page.size.width, height: page.size.height, drawingPoints: points); page.elements.add(e); selectedId = e.id; _changed(); return e; }")
CONTROLLER.write_text(controller, encoding='utf-8')

# Canvas: render new vector shapes, stock URLs and freehand drawings.
canvas = CANVAS.read_text(encoding='utf-8')
canvas = canvas.replace(
    "      case ElementKind.shape:\n        child = DecoratedBox(decoration: _decoration(e, isShape: true));\n        break;",
    "      case ElementKind.shape:\n        child = CustomPaint(painter: _ShapePainter(e), child: const SizedBox.expand());\n        break;\n      case ElementKind.drawing:\n        child = CustomPaint(painter: _DrawingPainter(e.drawingPoints, e.color, e.strokeWidth <= 0 ? 8 : e.strokeWidth), child: const SizedBox.expand());\n        break;")
canvas = canvas.replace(
    "child: e.imageBytes == null ? const ColoredBox(color: Colors.black12) : Image.memory(e.imageBytes!, fit: BoxFit.cover),",
    "child: e.imageBytes != null\n              ? Image.memory(e.imageBytes!, fit: BoxFit.cover)\n              : (e.imageUrl != null ? Image.network(e.imageUrl!, fit: BoxFit.cover, errorBuilder: (_, __, ___) => const ColoredBox(color: Colors.black12)) : const ColoredBox(color: Colors.black12)),")
canvas += r'''

class _ShapePainter extends CustomPainter {
  final DesignElement element;
  _ShapePainter(this.element);

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = element.color..style = PaintingStyle.fill;
    final stroke = Paint()..color = element.strokeColor..style = PaintingStyle.stroke..strokeWidth = element.strokeWidth;
    final rect = Offset.zero & size;
    switch (element.shapeType) {
      case 'circle':
        canvas.drawOval(rect, paint);
        if (element.strokeWidth > 0) canvas.drawOval(rect, stroke);
        break;
      case 'triangle':
        final path = Path()..moveTo(size.width / 2, 0)..lineTo(size.width, size.height)..lineTo(0, size.height)..close();
        canvas.drawPath(path, paint);
        if (element.strokeWidth > 0) canvas.drawPath(path, stroke);
        break;
      case 'diamond':
        final path = Path()..moveTo(size.width / 2, 0)..lineTo(size.width, size.height / 2)..lineTo(size.width / 2, size.height)..lineTo(0, size.height / 2)..close();
        canvas.drawPath(path, paint);
        if (element.strokeWidth > 0) canvas.drawPath(path, stroke);
        break;
      case 'star':
        final path = Path();
        const points = 10;
        for (var i = 0; i < points; i++) {
          final angle = -math.pi / 2 + i * math.pi / 5;
          final radius = i.isEven ? size.shortestSide / 2 : size.shortestSide / 4;
          final center = Offset(size.width / 2, size.height / 2);
          final p = center + Offset(math.cos(angle) * radius, math.sin(angle) * radius);
          if (i == 0) path.moveTo(p.dx, p.dy); else path.lineTo(p.dx, p.dy);
        }
        path.close();
        canvas.drawPath(path, paint);
        if (element.strokeWidth > 0) canvas.drawPath(path, stroke);
        break;
      case 'pill':
        canvas.drawRRect(RRect.fromRectAndRadius(rect, Radius.circular(size.shortestSide / 2)), paint);
        if (element.strokeWidth > 0) canvas.drawRRect(RRect.fromRectAndRadius(rect, Radius.circular(size.shortestSide / 2)), stroke);
        break;
      default:
        final radius = element.radius.clamp(0, size.shortestSide / 2);
        canvas.drawRRect(RRect.fromRectAndRadius(rect, Radius.circular(radius)), paint);
        if (element.strokeWidth > 0) canvas.drawRRect(RRect.fromRectAndRadius(rect, Radius.circular(radius)), stroke);
    }
  }

  @override
  bool shouldRepaint(covariant _ShapePainter oldDelegate) => oldDelegate.element != element || oldDelegate.element.colorValue != element.colorValue;
}

class _DrawingPainter extends CustomPainter {
  final List<Offset> points;
  final Color color;
  final double width;
  _DrawingPainter(this.points, this.color, this.width);

  @override
  void paint(Canvas canvas, Size size) {
    if (points.length < 2) return;
    final paint = Paint()..color = color..style = PaintingStyle.stroke..strokeCap = StrokeCap.round..strokeJoin = StrokeJoin.round..strokeWidth = width;
    final path = Path()..moveTo(points.first.dx, points.first.dy);
    for (var i = 1; i < points.length; i++) path.lineTo(points[i].dx, points[i].dy);
    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant _DrawingPainter oldDelegate) => oldDelegate.points != points || oldDelegate.color != color || oldDelegate.width != width;
}
'''
CANVAS.write_text(canvas, encoding='utf-8')

# Replace the generated Add New panel with real dedicated actions.
workspace = WORKSPACE.read_text(encoding='utf-8')
workspace = replace_method(workspace, '  Future<void> _addNewSheet()', r'''  Future<void> _addNewSheet() async {
    await showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      showDragHandle: true,
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(30))),
      builder: (sheetContext) {
        final items = <_AddNewItem>[
          _AddNewItem(Icons.photo_library_rounded, 'Gallery Pic', 'Import from gallery', _pickImage, const Color(0xFF2563EB)),
          _AddNewItem(Icons.collections_rounded, 'Stock Images', 'Curated stock library', _stockImagesSheet, const Color(0xFF5B5BEF)),
          _AddNewItem(Icons.folder_rounded, 'My Folder', 'Pick from device files', _folderImage, const Color(0xFF0EA5A8)),
          _AddNewItem(Icons.text_fields_rounded, 'Add Text', 'Advanced Urdu composer', _addText, const Color(0xFFF97316)),
          _AddNewItem(Icons.video_library_rounded, 'Video', 'Import video file', _videoPicker, const Color(0xFFE11D48)),
          _AddNewItem(Icons.music_note_rounded, 'Audio', 'Import audio file', _audioPicker, const Color(0xFF059669)),
          _AddNewItem(Icons.auto_awesome_rounded, 'AI Images', 'Prompt & creative brief', _aiImageSheet, const Color(0xFF7C3AED)),
          _AddNewItem(Icons.build_rounded, 'Tools', 'Real editing utilities', _toolsSheet, const Color(0xFF475569)),
          _AddNewItem(Icons.crop_square_rounded, 'Borders', 'Stroke & border studio', _bordersSheet, const Color(0xFFF59E0B)),
          _AddNewItem(Icons.grid_view_rounded, 'Table', 'Generate editable grid', _tableSheet, const Color(0xFF0D9488)),
          _AddNewItem(Icons.brush_rounded, 'Draw', 'Freehand drawing canvas', _drawSheet, const Color(0xFFE11D48)),
          _AddNewItem(Icons.edit_rounded, 'Pen Tool', 'Precision freehand path', _drawSheet, const Color(0xFF7C3AED)),
          _AddNewItem(Icons.business_rounded, 'Logos', 'Import a logo image', _folderImage, const Color(0xFF0D9488)),
          _AddNewItem(Icons.gesture_rounded, 'Special Text', 'Styled Urdu text presets', _specialTextSheet, const Color(0xFF0D9488)),
          _AddNewItem(Icons.category_rounded, 'Shapes', 'Vector shape library', _shapeSheet, const Color(0xFF0D9488)),
          _AddNewItem(Icons.star_rounded, 'PNG Images', 'Transparent PNG import', _folderImage, const Color(0xFF2563EB)),
          _AddNewItem(Icons.wallpaper_rounded, 'Backgrounds', 'Premium canvas backgrounds', _backgroundSheet, const Color(0xFF2563EB)),
        ];
        return SafeArea(
          child: SizedBox(
            height: MediaQuery.sizeOf(sheetContext).height * .86,
            child: Padding(
              padding: const EdgeInsets.fromLTRB(14, 2, 14, 14),
              child: Column(
                children: [
                  Row(children: [const Expanded(child: _SheetHeader('Add New', 'Every card opens its own real editing tool')), IconButton(onPressed: () => Navigator.pop(sheetContext), icon: const Icon(Icons.close_rounded))]),
                  const SizedBox(height: 6),
                  Expanded(
                    child: GridView.builder(
                      padding: const EdgeInsets.only(bottom: 8),
                      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount: 3, crossAxisSpacing: 10, mainAxisSpacing: 10, childAspectRatio: .92),
                      itemCount: items.length,
                      itemBuilder: (_, index) => _addNewCard(items[index], sheetContext),
                    ),
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Future<void> _stockImagesSheet() async {
    const urls = <String>[
      'https://images.unsplash.com/photo-1500534623283-312aade485b7?auto=format&fit=crop&w=1200&q=85',
      'https://images.unsplash.com/photo-1497366811353-6870744d04b2?auto=format&fit=crop&w=1200&q=85',
      'https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&w=1200&q=85',
      'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=85',
      'https://images.unsplash.com/photo-1470770841072-f978cf4d019e?auto=format&fit=crop&w=1200&q=85',
      'https://images.unsplash.com/photo-1518837695005-2083093ee35b?auto=format&fit=crop&w=1200&q=85',
      'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=1200&q=85',
      'https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=1200&q=85',
      'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=85',
    ];
    await showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      showDragHandle: true,
      builder: (sheetContext) => SafeArea(
        child: SizedBox(
          height: MediaQuery.sizeOf(sheetContext).height * .78,
          child: Column(children: [
            const _SheetHeader('Stock Images', 'Tap any image to place it on the canvas'),
            Expanded(child: GridView.builder(padding: const EdgeInsets.all(16), gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount: 3, crossAxisSpacing: 8, mainAxisSpacing: 8), itemCount: urls.length, itemBuilder: (_, i) => InkWell(onTap: () { controller.addImageUrl(urls[i]); Navigator.pop(sheetContext); }, child: ClipRRect(borderRadius: BorderRadius.circular(14), child: Image.network(urls[i], fit: BoxFit.cover, errorBuilder: (_, __, ___) => const ColoredBox(color: Colors.black12))))),
          ]),
        ),
      ),
    );
  }

  Future<void> _folderImage() async {
    final result = await FilePicker.platform.pickFiles(type: FileType.image, withData: true);
    final bytes = result?.files.single.bytes;
    if (bytes != null && bytes.isNotEmpty) controller.addImage(bytes);
  }

  Future<void> _videoPicker() async {
    final result = await FilePicker.platform.pickFiles(type: FileType.video, withData: false);
    if (!mounted || result == null) return;
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Video selected: ${result.files.single.name}')));
  }

  Future<void> _audioPicker() async {
    final result = await FilePicker.platform.pickFiles(type: FileType.audio, withData: false);
    if (!mounted || result == null) return;
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Audio selected: ${result.files.single.name}')));
  }

  Future<void> _aiImageSheet() async {
    final prompt = TextEditingController();
    final result = await showModalBottomSheet<String>(context: context, isScrollControlled: true, showDragHandle: true, builder: (sheetContext) => Padding(padding: EdgeInsets.fromLTRB(18, 8, 18, MediaQuery.viewInsetsOf(sheetContext).bottom + 22), child: Column(mainAxisSize: MainAxisSize.min, children: [const _SheetHeader('AI Image Studio', 'Write a detailed prompt for an image-generation workflow'), TextField(controller: prompt, maxLines: 4, textDirection: TextDirection.ltr, decoration: const InputDecoration(labelText: 'Prompt', hintText: 'e.g. luxury Islamic poster, gold calligraphy, dark background', border: OutlineInputBorder()),), const SizedBox(height: 12), SizedBox(width: double.infinity, child: FilledButton.icon(onPressed: () => Navigator.pop(sheetContext, prompt.text.trim()), icon: const Icon(Icons.auto_awesome_rounded), label: const Text('Create Prompt')))]));
    prompt.dispose();
    if (result != null && result.isNotEmpty && mounted) {
      await showDialog<void>(context: context, builder: (_) => AlertDialog(title: const Text('AI Prompt Ready'), content: SelectableText(result), actions: [TextButton(onPressed: () => Navigator.pop(context), child: const Text('Close'))]));
    }
  }

  Future<void> _toolsSheet() async {
    await showModalBottomSheet<void>(context: context, showDragHandle: true, builder: (sheetContext) => SafeArea(child: Wrap(children: [const _SheetHeader('Design Tools', 'Real actions for the selected object'), ListTile(leading: const Icon(Icons.copy_rounded), title: const Text('Duplicate'), onTap: () { controller.duplicateSelected(); Navigator.pop(sheetContext); }), ListTile(leading: const Icon(Icons.center_focus_strong_rounded), title: const Text('Center'), onTap: () { controller.centerSelected(); Navigator.pop(sheetContext); }), ListTile(leading: const Icon(Icons.flip_to_front_rounded), title: const Text('Bring Forward'), onTap: () { controller.bringSelectedForward(); Navigator.pop(sheetContext); }), ListTile(leading: const Icon(Icons.flip_to_back_rounded), title: const Text('Send Backward'), onTap: () { controller.sendSelectedBackward(); Navigator.pop(sheetContext); })])));
  }

  Future<void> _bordersSheet() async => _effectsSheet();

  Future<void> _shapeSheet() async {
    const shapes = <String, IconData>{'rectangle': Icons.crop_square_rounded, 'circle': Icons.circle_outlined, 'triangle': Icons.change_history_rounded, 'diamond': Icons.diamond_outlined, 'star': Icons.star_outline_rounded, 'pill': Icons.rectangle_rounded};
    final shape = await showModalBottomSheet<String>(context: context, showDragHandle: true, builder: (sheetContext) => SafeArea(child: GridView.count(shrinkWrap: true, crossAxisCount: 3, padding: const EdgeInsets.all(18), children: shapes.entries.map((entry) => InkWell(onTap: () => Navigator.pop(sheetContext, entry.key), child: Card(child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [Icon(entry.value, size: 34, color: _primary), const SizedBox(height: 6), Text(entry.key, style: const TextStyle(fontWeight: FontWeight.w800))])))).toList()));
    if (shape != null) controller.addShape(shapeType: shape);
  }

  Future<void> _tableSheet() async {
    int rows = 3;
    int cols = 3;
    await showModalBottomSheet<void>(context: context, showDragHandle: true, builder: (sheetContext) => StatefulBuilder(builder: (_, setState) => SafeArea(child: Padding(padding: const EdgeInsets.fromLTRB(18, 8, 18, 22), child: Column(mainAxisSize: MainAxisSize.min, children: [const _SheetHeader('Table Builder', 'Generate a clean editable grid on the canvas'), Row(children: [Expanded(child: Text('Rows: $rows')), Expanded(child: Text('Columns: $cols'))]), Slider(min: 1, max: 10, divisions: 9, value: rows.toDouble(), onChanged: (v) => setState(() => rows = v.round())), Slider(min: 1, max: 10, divisions: 9, value: cols.toDouble(), onChanged: (v) => setState(() => cols = v.round())), SizedBox(width: double.infinity, child: FilledButton.icon(onPressed: () { final cellW = controller.page.size.width / cols; final cellH = 70.0; for (var r = 0; r < rows; r++) { for (var c = 0; c < cols; c++) { final e = controller.addShape(shapeType: 'rectangle'); e.x = c * cellW; e.y = r * cellH; e.width = cellW; e.height = cellH; e.radius = 0; e.colorValue = Colors.transparent.toARGB32(); e.strokeWidth = 2; e.strokeColorValue = Colors.black.toARGB32(); } } Navigator.pop(sheetContext); }, icon: const Icon(Icons.grid_3x3_rounded), label: const Text('Create Table')))]))));
  }

  Future<void> _drawSheet() async {
    final points = <Offset>[];
    await showDialog<void>(context: context, builder: (dialogContext) => Dialog.fullscreen(child: StatefulBuilder(builder: (_, setState) => Scaffold(appBar: AppBar(title: const Text('Draw Studio'), actions: [IconButton(onPressed: () { if (points.length > 1) controller.addDrawing(List<Offset>.from(points)); Navigator.pop(dialogContext); }, icon: const Icon(Icons.check_rounded))]), body: GestureDetector(behavior: HitTestBehavior.opaque, onPanStart: (d) => setState(() => points.add(d.localPosition)), onPanUpdate: (d) => setState(() => points.add(d.localPosition)), child: CustomPaint(painter: _LiveDrawingPainter(points), child: const SizedBox.expand()))))));
  }

  Future<void> _specialTextSheet() async {
    final value = await _textDialog('Special Text', 'اپنا خوبصورت اردو متن یہاں لکھیں');
    if (value != null && value.trim().isNotEmpty) {
      final e = controller.addText(text: value.trim());
      controller.updateSelected(colorValue: const Color(0xFFD4AF37).toARGB32());
      if (e.bold == false) controller.toggleSelectedBold();
    }
  }
''')

# Add file-picker import if the reference panel did not leave it available.
workspace = workspace.replace("import 'package:image_picker/image_picker.dart';", "import 'package:image_picker/image_picker.dart';\nimport 'package:file_picker/file_picker.dart';")
WORKSPACE.write_text(workspace, encoding='utf-8')

# Add a tiny live drawing painter to workspace (Dialog preview only).
ws = WORKSPACE.read_text(encoding='utf-8')
if 'class _LiveDrawingPainter' not in ws:
    ws = ws.rstrip() + r'''

class _LiveDrawingPainter extends CustomPainter {
  final List<Offset> points;
  _LiveDrawingPainter(this.points);
  @override
  void paint(Canvas canvas, Size size) {
    if (points.length < 2) return;
    final paint = Paint()..color = const Color(0xFF6D28D9)..strokeWidth = 7..strokeCap = StrokeCap.round..style = PaintingStyle.stroke;
    final path = Path()..moveTo(points.first.dx, points.first.dy);
    for (var i = 1; i < points.length; i++) path.lineTo(points[i].dx, points[i].dy);
    canvas.drawPath(path, paint);
  }
  @override
  bool shouldRepaint(covariant _LiveDrawingPainter oldDelegate) => oldDelegate.points != points;
}
'''
    WORKSPACE.write_text(ws, encoding='utf-8')

print('Applied real Add New tools: stock URLs, file import, vector shapes, tables, drawing, and dedicated tool panels.')