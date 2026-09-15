from pathlib import Path
import re

# Persistent model upgrade: image fit/crop/flip state is part of project JSON.
model = Path('lib/models/design_models.dart')
text = model.read_text()
if 'String imageFit;' not in text:
    text = text.replace('  double radius;\n', '  double radius;\n  String imageFit;\n  bool flipX, flipY;\n  double imageZoom, imageOffsetX, imageOffsetY;\n')
    text = text.replace('    this.radius = 18,\n', "    this.radius = 18,\n    this.imageFit = 'cover',\n    this.flipX = false,\n    this.flipY = false,\n    this.imageZoom = 1,\n    this.imageOffsetX = 0,\n    this.imageOffsetY = 0,\n")
    text = text.replace("'imageBytes': imageBytes == null ? null : base64Encode(imageBytes!), 'radius': radius,", "'imageBytes': imageBytes == null ? null : base64Encode(imageBytes!), 'radius': radius,\n        'imageFit': imageFit, 'flipX': flipX, 'flipY': flipY,\n        'imageZoom': imageZoom, 'imageOffsetX': imageOffsetX, 'imageOffsetY': imageOffsetY,")
    text = text.replace("imageBytes: bytes, radius: (json['radius'] as num?)?.toDouble() ?? 18,", "imageBytes: bytes, radius: (json['radius'] as num?)?.toDouble() ?? 18,\n      imageFit: ['cover', 'contain', 'fill'].contains(json['imageFit']) ? json['imageFit'].toString() : 'cover',\n      flipX: json['flipX'] as bool? ?? false, flipY: json['flipY'] as bool? ?? false,\n      imageZoom: ((json['imageZoom'] as num?)?.toDouble() ?? 1).clamp(1, 4),\n      imageOffsetX: ((json['imageOffsetX'] as num?)?.toDouble() ?? 0).clamp(-1, 1),\n      imageOffsetY: ((json['imageOffsetY'] as num?)?.toDouble() ?? 0).clamp(-1, 1),")
    text = text.replace('const int kSchemaVersion = 3;', 'const int kSchemaVersion = 4;')
    model.write_text(text)

# Controller actions: single undo checkpoint per applied Image Studio operation.
controller = Path('lib/state/workspace_controller.dart')
text = controller.read_text()
if 'setSelectedImageFit' not in text:
    needle = '  void replaceSelectedImage(Uint8List bytes) { final e = selected; if (e == null || e.kind != ElementKind.image || e.locked) return; _checkpoint(); e.imageBytes = bytes; _changed(); }\n'
    methods = needle + '''\n  void setSelectedImageFit(String fit) {\n    final e = selected;\n    if (e == null || e.kind != ElementKind.image || e.locked) return;\n    if (!['cover', 'contain', 'fill'].contains(fit) || e.imageFit == fit) return;\n    _checkpoint(); e.imageFit = fit; _changed();\n  }\n\n  void setSelectedImageZoom(double value) {\n    final e = selected;\n    if (e == null || e.kind != ElementKind.image || e.locked) return;\n    _checkpoint(); e.imageZoom = value.clamp(1, 4).toDouble(); _changed();\n  }\n\n  void setSelectedImagePosition({double? x, double? y}) {\n    final e = selected;\n    if (e == null || e.kind != ElementKind.image || e.locked) return;\n    _checkpoint();\n    if (x != null) e.imageOffsetX = x.clamp(-1, 1).toDouble();\n    if (y != null) e.imageOffsetY = y.clamp(-1, 1).toDouble();\n    _changed();\n  }\n\n  void toggleSelectedImageFlipX() {\n    final e = selected;\n    if (e == null || e.kind != ElementKind.image || e.locked) return;\n    _checkpoint(); e.flipX = !e.flipX; _changed();\n  }\n\n  void toggleSelectedImageFlipY() {\n    final e = selected;\n    if (e == null || e.kind != ElementKind.image || e.locked) return;\n    _checkpoint(); e.flipY = !e.flipY; _changed();\n  }\n\n  void resetSelectedImage() {\n    final e = selected;\n    if (e == null || e.kind != ElementKind.image || e.locked) return;\n    _checkpoint(); e.imageFit = 'cover'; e.flipX = false; e.flipY = false; e.imageZoom = 1; e.imageOffsetX = 0; e.imageOffsetY = 0; _changed();\n  }\n'''
    if needle not in text:
        raise SystemExit('image replace method not found')
    text = text.replace(needle, methods, 1)
    controller.write_text(text)

# Canvas rendering: crop/fit/zoom/position + independent horizontal/vertical flip.
canvas = Path('lib/widgets/design_canvas.dart')
text = canvas.read_text()
old = "child: e.imageBytes == null ? const ColoredBox(color: Colors.black12) : Image.memory(e.imageBytes!, fit: BoxFit.cover),"
new = '''child: e.imageBytes == null
              ? const ColoredBox(color: Colors.black12)
              : ClipRect(
                  child: Transform(
                    alignment: Alignment.center,
                    transform: Matrix4.diagonal3Values(e.flipX ? -e.imageZoom : e.imageZoom, e.flipY ? -e.imageZoom : e.imageZoom, 1),
                    child: Image.memory(
                      e.imageBytes!,
                      fit: e.imageFit == 'contain' ? BoxFit.contain : e.imageFit == 'fill' ? BoxFit.fill : BoxFit.cover,
                      alignment: Alignment(e.imageOffsetX, e.imageOffsetY),
                      width: e.width,
                      height: e.height,
                      filterQuality: FilterQuality.high,
                    ),
                  ),
                ),'''
if old in text:
    text = text.replace(old, new, 1)
canvas.write_text(text)

# Generated toolbar: add Image Studio entry and sheet.
workspace = Path('lib/screens/workspace_screen.dart')
text = workspace.read_text()
text = text.replace("    final isShape = element.kind == ElementKind.shape;\n    final tools = <Widget>[", "    final isShape = element.kind == ElementKind.shape;\n    final isImage = element.kind == ElementKind.image;\n    final tools = <Widget>[", 1)
text = text.replace("      if (isText) _tool(Icons.edit_rounded, 'Edit', _editText),\n", "      if (isText) _tool(Icons.edit_rounded, 'Edit', _editText),\n      if (isImage) _tool(Icons.crop_rounded, 'Image', _imageStudioSheet),\n", 1)
text = text.replace("  Future<void> _moreSheet() async {", '''  Future<void> _imageStudioSheet() async {
    final element = controller.selected;
    if (element == null || element.kind != ElementKind.image) return;
    var zoom = element.imageZoom;
    var offsetX = element.imageOffsetX;
    var offsetY = element.imageOffsetY;
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
                const _SheetHeader('Image Studio', 'Professional crop, fit, position and flip controls'),
                const SizedBox(height: 6),
                Row(children: [
                  Expanded(child: _imageStudioButton('Cover', Icons.crop_rounded, element.imageFit == 'cover', () { controller.setSelectedImageFit('cover'); setSheetState(() {}); })),
                  const SizedBox(width: 8),
                  Expanded(child: _imageStudioButton('Contain', Icons.fit_screen_rounded, element.imageFit == 'contain', () { controller.setSelectedImageFit('contain'); setSheetState(() {}); })),
                  const SizedBox(width: 8),
                  Expanded(child: _imageStudioButton('Fill', Icons.fullscreen_rounded, element.imageFit == 'fill', () { controller.setSelectedImageFit('fill'); setSheetState(() {}); })),
                ]),
                const SizedBox(height: 10),
                _effectSlider('Crop Zoom', zoom, 1, 4, (v) => setSheetState(() => zoom = v)),
                _effectSlider('Horizontal Position', offsetX, -1, 1, (v) => setSheetState(() => offsetX = v)),
                _effectSlider('Vertical Position', offsetY, -1, 1, (v) => setSheetState(() => offsetY = v)),
                const SizedBox(height: 4),
                Row(children: [
                  Expanded(child: OutlinedButton.icon(onPressed: () { controller.toggleSelectedImageFlipX(); setSheetState(() {}); }, icon: const Icon(Icons.flip_rounded), label: const Text('Flip H'))),
                  const SizedBox(width: 8),
                  Expanded(child: OutlinedButton.icon(onPressed: () { controller.toggleSelectedImageFlipY(); setSheetState(() {}); }, icon: const Icon(Icons.flip_rounded), label: const Text('Flip V'))),
                ]),
                const SizedBox(height: 8),
                SizedBox(width: double.infinity, child: FilledButton.icon(
                  onPressed: () { controller.setSelectedImageZoom(zoom); controller.setSelectedImagePosition(x: offsetX, y: offsetY); Navigator.pop(sheetContext); },
                  icon: const Icon(Icons.check_rounded), label: const Text('Apply image adjustments'),
                )),
                TextButton.icon(onPressed: () { controller.resetSelectedImage(); Navigator.pop(sheetContext); }, icon: const Icon(Icons.restart_alt_rounded), label: const Text('Reset image')),
              ]),
            ),
          ),
        ),
      ),
    );
  }

  Widget _imageStudioButton(String label, IconData icon, bool active, VoidCallback onTap) {
    return OutlinedButton.icon(
      onPressed: onTap,
      icon: Icon(icon, size: 18),
      label: Text(label),
      style: OutlinedButton.styleFrom(backgroundColor: active ? _primary.withValues(alpha: .10) : null, foregroundColor: active ? _primary : null, padding: const EdgeInsets.symmetric(vertical: 12)),
    );
  }

  Future<void> _moreSheet() async {''', 1)
workspace.write_text(text)
print('Image Studio upgrade applied')
