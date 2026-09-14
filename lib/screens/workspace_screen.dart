import 'dart:typed_data';

import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../data/project_repository.dart';
import '../models/design_models.dart';
import '../services/export_service.dart';
import '../state/workspace_controller.dart';
import '../widgets/design_canvas.dart';

class WorkspaceScreen extends StatefulWidget {
  final CanvasSize? size;
  final ProjectModel? initialProject;

  const WorkspaceScreen({super.key, this.size, this.initialProject});

  @override
  State<WorkspaceScreen> createState() => _WorkspaceScreenState();
}

class _WorkspaceScreenState extends State<WorkspaceScreen> {
  late final WorkspaceController controller;
  final GlobalKey _canvasKey = GlobalKey();
  final ExportService _exportService = ExportService();
  final ProjectRepository _repository = ProjectRepository();
  final ImagePicker _imagePicker = ImagePicker();
  final TransformationController _viewTransform = TransformationController();

  static const _purple = Color(0xFF6D28D9);
  static const _ink = Color(0xFF171326);
  static const _surface = Color(0xFFF4F3F8);

  @override
  void initState() {
    super.initState();
    controller = WorkspaceController(initial: widget.initialProject, newSize: widget.size);
  }

  @override
  void dispose() {
    _viewTransform.dispose();
    controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: controller,
      builder: (context, _) => Scaffold(
        backgroundColor: _surface,
        appBar: _appBar(),
        body: Column(children: [Expanded(child: _editorArea()), _bottomToolbar()]),
      ),
    );
  }

  PreferredSizeWidget _appBar() {
    return AppBar(
      elevation: 0,
      backgroundColor: Colors.white,
      surfaceTintColor: Colors.white,
      titleSpacing: 2,
      leading: IconButton(
        tooltip: 'Back',
        icon: const Icon(Icons.arrow_back_rounded),
        onPressed: () => Navigator.pop(context),
      ),
      title: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(controller.project.name, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w900, color: _ink)),
          Text('Page ${controller.currentPageIndex + 1}  •  ${controller.page.size.width.toInt()} × ${controller.page.size.height.toInt()}', style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w600, color: Colors.black54)),
        ],
      ),
      actions: [
        IconButton(tooltip: 'Save', onPressed: _saveProject, icon: const Icon(Icons.save_outlined)),
        IconButton(tooltip: 'Undo', onPressed: controller.canUndo ? controller.undo : null, icon: const Icon(Icons.undo_rounded)),
        IconButton(tooltip: 'Redo', onPressed: controller.canRedo ? controller.redo : null, icon: const Icon(Icons.redo_rounded)),
        PopupMenuButton<String>(
          tooltip: 'Export',
          onSelected: _handleMenu,
          itemBuilder: (context) => const [
            PopupMenuItem(value: 'png', child: Text('Export PNG')),
            PopupMenuItem(value: 'jpg', child: Text('Export JPG')),
            PopupMenuItem(value: 'pdf', child: Text('Share PDF')),
          ],
        ),
      ],
    );
  }

  Widget _editorArea() {
    final page = controller.page;
    return LayoutBuilder(
      builder: (context, constraints) {
        final width = (constraints.maxWidth - 28).clamp(120.0, double.infinity);
        final height = (constraints.maxHeight - 28).clamp(120.0, double.infinity);
        final baseScale = (width / page.size.width < height / page.size.height ? width / page.size.width : height / page.size.height).clamp(.05, 1.0);
        return AnimatedBuilder(
          animation: _viewTransform,
          builder: (context, _) {
            final zoom = _viewTransform.value.getMaxScaleOnAxis().clamp(.5, 4.0);
            return Padding(
              padding: const EdgeInsets.all(14),
              child: Stack(
                children: [
                  Positioned.fill(
                    child: InteractiveViewer(
                      transformationController: _viewTransform,
                      minScale: .5,
                      maxScale: 4,
                      constrained: false,
                      boundaryMargin: const EdgeInsets.all(220),
                      child: Center(
                        child: SizedBox(
                          width: width,
                          height: height,
                          child: FittedBox(
                            fit: BoxFit.contain,
                            alignment: Alignment.center,
                            child: DesignCanvas(controller: controller, repaintKey: _canvasKey, interactionScale: baseScale * zoom),
                          ),
                        ),
                      ),
                    ),
                  ),
                  Positioned(
                    top: 8,
                    right: 8,
                    child: _floatingButton(Icons.center_focus_strong_rounded, 'Reset zoom', () => _viewTransform.value = Matrix4.identity()),
                  ),
                  Positioned(
                    left: 8,
                    bottom: 8,
                    child: _zoomBadge(zoom),
                  ),
                ],
              ),
            );
          },
        );
      },
    );
  }

  Widget _floatingButton(IconData icon, String tooltip, VoidCallback onTap) {
    return Material(
      color: Colors.white,
      elevation: 3,
      shadowColor: Colors.black26,
      borderRadius: BorderRadius.circular(13),
      child: IconButton(tooltip: tooltip, onPressed: onTap, icon: Icon(icon, size: 21)),
    );
  }

  Widget _zoomBadge(double zoom) {
    return Material(
      color: Colors.white,
      elevation: 2,
      borderRadius: BorderRadius.circular(18),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 11, vertical: 7),
        child: Text('${(zoom * 100).round()}%', style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800)),
      ),
    );
  }

  Widget _bottomToolbar() {
    final selected = controller.selected;
    return SafeArea(
      top: false,
      child: Container(
        decoration: const BoxDecoration(
          color: Colors.white,
          boxShadow: [BoxShadow(blurRadius: 18, offset: Offset(0, -5), color: Color(0x1A000000))],
        ),
        padding: const EdgeInsets.fromLTRB(10, 7, 10, 8),
        child: selected == null ? _mainTools() : _contextualTools(selected),
      ),
    );
  }

  Widget _mainTools() {
    return Row(
      children: [
        _primaryTool(Icons.text_fields_rounded, 'Text', _addText),
        _primaryTool(Icons.crop_square_rounded, 'Shape', () => controller.addShape()),
        _primaryTool(Icons.image_outlined, 'Image', _pickImage),
        _primaryTool(Icons.layers_outlined, 'Pages', _showPages),
        _primaryTool(Icons.tune_rounded, 'Design', _showDesignTools),
      ],
    );
  }

  Widget _contextualTools(DesignElement e) {
    final isText = e.kind == ElementKind.text;
    final isShape = e.kind == ElementKind.shape;
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        SizedBox(
          height: 58,
          child: ListView(
            scrollDirection: Axis.horizontal,
            children: [
              if (isText) _contextTool(Icons.edit_rounded, 'Edit', _editText),
              if (isText) _contextTool(Icons.font_download_outlined, 'Font', _fontDialog),
              if (isText) _contextTool(Icons.format_size_rounded, '${e.fontSize.round()}', () => _fontSizeDialog(e)),
              if (isText) _toggleTool(Icons.format_bold_rounded, 'Bold', e.bold, controller.toggleSelectedBold),
              if (isText) _toggleTool(Icons.format_italic_rounded, 'Italic', e.italic, controller.toggleSelectedItalic),
              _contextTool(Icons.palette_outlined, 'Color', _colorDialog),
              if (isShape) _contextTool(Icons.rounded_corner, 'Corners', _radiusDialog),
              _contextTool(Icons.opacity_rounded, 'Opacity', _opacityDialog),
              if (isText) _contextTool(Icons.format_align_center_rounded, 'Align', _alignmentDialog),
              if (isText) _contextTool(Icons.translate_rounded, 'Direction', _directionDialog),
              _contextTool(Icons.open_with_rounded, 'Arrange', _arrangeDialog),
              _contextTool(Icons.more_horiz_rounded, 'More', _showSelectedMore),
            ],
          ),
        ),
        const SizedBox(height: 2),
        Row(
          children: [
            Expanded(
              child: Row(
                children: [
                  Container(width: 8, height: 8, decoration: const BoxDecoration(color: _purple, shape: BoxShape.circle)),
                  const SizedBox(width: 7),
                  Expanded(child: Text(_selectionLabel(e), maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800))),
                ],
              ),
            ),
            _quickIcon(Icons.copy_outlined, 'Duplicate', controller.duplicateSelected),
            _quickIcon(e.locked ? Icons.lock_rounded : Icons.lock_open_rounded, e.locked ? 'Unlock' : 'Lock', controller.toggleSelectedLock),
            _quickIcon(Icons.delete_outline_rounded, 'Delete', controller.deleteSelected),
          ],
        ),
      ],
    );
  }

  String _selectionLabel(DesignElement e) {
    if (e.kind == ElementKind.text) return 'Urdu Text  •  ${e.fontFamily == 'JameelNoori' ? 'Gulzar' : e.fontFamily}';
    if (e.kind == ElementKind.image) return 'Image  •  ${e.width.toInt()} × ${e.height.toInt()}';
    return 'Shape  •  ${e.width.toInt()} × ${e.height.toInt()}';
  }

  Widget _primaryTool(IconData icon, String label, VoidCallback onTap) {
    return Expanded(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(14),
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 5),
          child: Column(children: [Icon(icon, size: 25, color: _purple), const SizedBox(height: 4), Text(label, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800))]),
        ),
      ),
    );
  }

  Widget _contextTool(IconData icon, String label, VoidCallback onTap) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 3),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(12),
          child: SizedBox(
            width: 62,
            child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [Icon(icon, size: 21, color: _purple), const SizedBox(height: 3), Text(label, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 9, fontWeight: FontWeight.w800))]),
          ),
        ),
      ),
    );
  }

  Widget _toggleTool(IconData icon, String label, bool active, VoidCallback onTap) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 3),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Container(
          width: 62,
          decoration: BoxDecoration(color: active ? _purple.withValues(alpha: .10) : Colors.transparent, borderRadius: BorderRadius.circular(12)),
          child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [Icon(icon, size: 21, color: active ? _purple : Colors.black54), const SizedBox(height: 3), Text(label, style: TextStyle(fontSize: 9, fontWeight: FontWeight.w800, color: active ? _purple : Colors.black87))]),
        ),
      ),
    );
  }

  Widget _quickIcon(IconData icon, String tooltip, VoidCallback onTap) => IconButton(tooltip: tooltip, visualDensity: VisualDensity.compact, onPressed: onTap, icon: Icon(icon, size: 21));

  Future<void> _addText() async {
    final text = await _textDialog(initial: 'اپنا متن یہاں لکھیں');
    if (text != null && text.trim().isNotEmpty) controller.addText(text: text.trim());
  }

  Future<void> _editText() async {
    final e = controller.selected;
    if (e == null) return;
    final text = await _textDialog(initial: e.text);
    if (text != null) controller.editSelectedText(text);
  }

  Future<String?> _textDialog({required String initial}) async {
    final textController = TextEditingController(text: initial);
    final result = await showDialog<String>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Urdu Text', style: TextStyle(fontWeight: FontWeight.w900)),
        content: TextField(
          controller: textController,
          autofocus: true,
          maxLines: 7,
          textDirection: TextDirection.rtl,
          style: const TextStyle(fontFamily: 'Gulzar', fontSize: 23),
          decoration: const InputDecoration(hintText: 'اپنا متن یہاں لکھیں', border: OutlineInputBorder()),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(dialogContext), child: const Text('Cancel')),
          FilledButton(onPressed: () => Navigator.pop(dialogContext, textController.text), child: const Text('Apply')),
        ],
      ),
    );
    textController.dispose();
    return result;
  }

  Future<void> _fontDialog() async {
    final e = controller.selected;
    if (e == null) return;
    final result = await showModalBottomSheet<String>(
      context: context,
      showDragHandle: true,
      builder: (context) => SafeArea(
        child: ListView(shrinkWrap: true, children: [
          const _SheetHeader(title: 'Urdu Fonts', subtitle: 'Choose a Nastaliq family'),
          _fontTile('Gulzar', 'Contemporary Nastaliq', 'Gulzar', e.fontFamily),
          _fontTile('Noto Nastaliq Urdu', 'Google Fonts Nastaliq', 'NotoNastaliqUrdu', e.fontFamily),
        ]),
      ),
    );
    if (result != null) controller.setSelectedFont(result);
  }

  Widget _fontTile(String title, String subtitle, String family, String current) {
    final selected = current == family || (current == 'JameelNoori' && family == 'Gulzar');
    return ListTile(
      leading: CircleAvatar(backgroundColor: selected ? _purple : Colors.black12, child: Icon(Icons.font_download_rounded, color: selected ? Colors.white : Colors.black54)),
      title: Text(title, style: TextStyle(fontFamily: family, fontSize: 22, fontWeight: FontWeight.w700)),
      subtitle: Text(subtitle),
      trailing: selected ? const Icon(Icons.check_circle_rounded, color: _purple) : null,
      onTap: () => Navigator.pop(context, family),
    );
  }

  Future<void> _fontSizeDialog(DesignElement e) async {
    double value = e.fontSize;
    final result = await showDialog<double>(
      context: context,
      builder: (dialogContext) => StatefulBuilder(
        builder: (context, setState) => AlertDialog(
          title: const Text('Font Size', style: TextStyle(fontWeight: FontWeight.w900)),
          content: Column(mainAxisSize: MainAxisSize.min, children: [
            Text('${value.round()} px', style: const TextStyle(fontSize: 26, fontWeight: FontWeight.w900, color: _purple)),
            Slider(min: 8, max: 300, divisions: 73, value: value.clamp(8, 300), onChanged: (v) => setState(() => value = v)),
          ]),
          actions: [TextButton(onPressed: () => Navigator.pop(dialogContext), child: const Text('Cancel')), FilledButton(onPressed: () => Navigator.pop(dialogContext, value), child: const Text('Apply'))],
        ),
      ),
    );
    if (result != null) controller.setSelectedFontSize(result);
  }

  Future<void> _alignmentDialog() async {
    final e = controller.selected;
    if (e == null) return;
    final result = await showModalBottomSheet<TextAlign>(
      context: context,
      showDragHandle: true,
      builder: (context) => SafeArea(child: Column(mainAxisSize: MainAxisSize.min, children: [
        const _SheetHeader(title: 'Text Alignment', subtitle: 'Control how the Urdu text sits inside its box'),
        _choiceTile('Left', Icons.format_align_left_rounded, TextAlign.left, e.textAlign),
        _choiceTile('Center', Icons.format_align_center_rounded, TextAlign.center, e.textAlign),
        _choiceTile('Right', Icons.format_align_right_rounded, TextAlign.right, e.textAlign),
        _choiceTile('Justify', Icons.format_align_justify_rounded, TextAlign.justify, e.textAlign),
        const SizedBox(height: 10),
      ])),
    );
    if (result != null) controller.setSelectedAlign(result);
  }

  Widget _choiceTile(String title, IconData icon, TextAlign value, TextAlign current) => ListTile(leading: Icon(icon), title: Text(title), trailing: value == current ? const Icon(Icons.check_rounded, color: _purple) : null, onTap: () => Navigator.pop(context, value));

  Future<void> _directionDialog() async {
    final e = controller.selected;
    if (e == null) return;
    final result = await showModalBottomSheet<TextDirection>(
      context: context,
      showDragHandle: true,
      builder: (context) => SafeArea(child: Column(mainAxisSize: MainAxisSize.min, children: [
        const _SheetHeader(title: 'Text Direction', subtitle: 'Use RTL for Urdu and Arabic writing'),
        _directionTile('Right to Left (RTL)', TextDirection.rtl, e.textDirection, 'Urdu / Arabic'),
        _directionTile('Left to Right (LTR)', TextDirection.ltr, e.textDirection, 'English / Latin'),
        const SizedBox(height: 12),
      ])),
    );
    if (result != null) controller.setSelectedDirection(result);
  }

  Widget _directionTile(String title, TextDirection value, TextDirection current, String subtitle) => ListTile(leading: Icon(value == TextDirection.rtl ? Icons.format_textdirection_r_to_l : Icons.format_textdirection_l_to_r), title: Text(title), subtitle: Text(subtitle), trailing: value == current ? const Icon(Icons.check_rounded, color: _purple) : null, onTap: () => Navigator.pop(context, value));

  Future<void> _colorDialog() async {
    final colors = <Color>[
      Colors.black,
      Colors.white,
      const Color(0xFFD4AF37),
      const Color(0xFF7C3AED),
      const Color(0xFF2563EB),
      const Color(0xFFDC2626),
      const Color(0xFF059669),
      const Color(0xFFF59E0B),
      const Color(0xFFEC4899),
      const Color(0xFF0F766E),
      const Color(0xFF334155),
      const Color(0xFF7F1D1D),
    ];
    await showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      builder: (context) => SafeArea(child: Padding(padding: const EdgeInsets.fromLTRB(20, 4, 20, 24), child: Column(mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.start, children: [
        const _SheetHeader(title: 'Color', subtitle: 'Choose a clean, print-friendly color'),
        Wrap(spacing: 13, runSpacing: 13, children: [for (final color in colors) _colorChip(color)]),
      ]))),
    );
  }

  Widget _colorChip(Color color) {
    final current = controller.selected?.colorValue == color.toARGB32();
    return GestureDetector(
      onTap: () { controller.updateSelected(colorValue: color.toARGB32()); Navigator.pop(context); },
      child: Container(width: 48, height: 48, decoration: BoxDecoration(color: color, shape: BoxShape.circle, border: Border.all(color: current ? _purple : Colors.black12, width: current ? 3 : 1.5), boxShadow: const [BoxShadow(blurRadius: 4, color: Color(0x18000000))]), child: current ? Icon(Icons.check_rounded, color: color.computeLuminance() > .55 ? Colors.black : Colors.white) : null),
    );
  }

  Future<void> _opacityDialog() async {
    final e = controller.selected;
    if (e == null) return;
    double value = e.opacity;
    final result = await showDialog<double>(
      context: context,
      builder: (dialogContext) => StatefulBuilder(
        builder: (context, setState) => AlertDialog(
          title: const Text('Opacity', style: TextStyle(fontWeight: FontWeight.w900)),
          content: Column(mainAxisSize: MainAxisSize.min, children: [Text('${(value * 100).round()}%', style: const TextStyle(fontSize: 26, fontWeight: FontWeight.w900, color: _purple)), Slider(min: 0, max: 1, divisions: 20, value: value, onChanged: (v) => setState(() => value = v))]),
          actions: [TextButton(onPressed: () => Navigator.pop(dialogContext), child: const Text('Cancel')), FilledButton(onPressed: () => Navigator.pop(dialogContext, value), child: const Text('Apply'))],
        ),
      ),
    );
    if (result != null) controller.setSelectedOpacity(result);
  }

  Future<void> _radiusDialog() async {
    final e = controller.selected;
    if (e == null) return;
    double value = e.radius;
    final result = await showDialog<double>(
      context: context,
      builder: (dialogContext) => StatefulBuilder(
        builder: (context, setState) => AlertDialog(
          title: const Text('Corner Radius', style: TextStyle(fontWeight: FontWeight.w900)),
          content: Column(mainAxisSize: MainAxisSize.min, children: [Text('${value.round()} px', style: const TextStyle(fontSize: 24, fontWeight: FontWeight.w900, color: _purple)), Slider(min: 0, max: 240, divisions: 24, value: value.clamp(0, 240), onChanged: (v) => setState(() => value = v))]),
          actions: [TextButton(onPressed: () => Navigator.pop(dialogContext), child: const Text('Cancel')), FilledButton(onPressed: () => Navigator.pop(dialogContext, value), child: const Text('Apply'))],
        ),
      ),
    );
    if (result != null) controller.setSelectedRadius(result);
  }

  Future<void> _arrangeDialog() async {
    final e = controller.selected;
    if (e == null) return;
    await showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      builder: (context) => SafeArea(child: Wrap(children: [
        const _SheetHeader(title: 'Arrange', subtitle: 'Position, rotation and layer order'),
        ListTile(leading: const Icon(Icons.center_focus_strong_rounded), title: const Text('Center on canvas'), onTap: () { controller.centerSelected(); Navigator.pop(context); }),
        ListTile(leading: const Icon(Icons.rotate_90_degrees_ccw_rounded), title: const Text('Reset rotation'), onTap: () { controller.resetSelectedRotation(); Navigator.pop(context); }),
        ListTile(leading: const Icon(Icons.rotate_right_rounded), title: const Text('Rotation presets'), onTap: () { Navigator.pop(context); _rotationDialog(); }),
        ListTile(leading: const Icon(Icons.vertical_align_top_rounded), title: const Text('Bring to front'), onTap: () { controller.bringSelectedToFront(); Navigator.pop(context); }),
        ListTile(leading: const Icon(Icons.vertical_align_bottom_rounded), title: const Text('Send to back'), onTap: () { controller.sendSelectedToBack(); Navigator.pop(context); }),
      ])),
    );
  }

  Future<void> _rotationDialog() async {
    final e = controller.selected;
    if (e == null) return;
    const options = <double>[0, 0.785398, 1.570796, 3.141593, -1.570796, -0.785398];
    final labels = <String>['0°', '45°', '90°', '180°', '-90°', '-45°'];
    final result = await showModalBottomSheet<double>(
      context: context,
      showDragHandle: true,
      builder: (context) => SafeArea(child: Column(mainAxisSize: MainAxisSize.min, children: [
        const _SheetHeader(title: 'Rotation', subtitle: 'Quick angle presets'),
        for (var i = 0; i < options.length; i++) ListTile(leading: const Icon(Icons.rotate_right_rounded), title: Text(labels[i]), trailing: (e.rotation - options[i]).abs() < .03 ? const Icon(Icons.check_rounded, color: _purple) : null, onTap: () => Navigator.pop(context, options[i])),
        const SizedBox(height: 8),
      ])),
    );
    if (result != null) controller.rotateSelectedTo(result);
  }

  Future<void> _showSelectedMore() async {
    final e = controller.selected;
    if (e == null) return;
    await showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      builder: (context) => SafeArea(child: Wrap(children: [
        const _SheetHeader(title: 'More options', subtitle: 'Actions for the selected element'),
        ListTile(leading: const Icon(Icons.open_with_rounded), title: const Text('Transform & size'), onTap: () { Navigator.pop(context); _transformDialog(); }),
        if (e.kind == ElementKind.image) ListTile(leading: const Icon(Icons.image_search_rounded), title: const Text('Replace image'), onTap: () { Navigator.pop(context); _replaceImage(); }),
        ListTile(leading: Icon(e.hidden ? Icons.visibility_rounded : Icons.visibility_off_outlined), title: Text(e.hidden ? 'Show element' : 'Hide element'), onTap: () { controller.toggleSelectedHidden(); Navigator.pop(context); }),
        ListTile(leading: Icon(e.locked ? Icons.lock_open_rounded : Icons.lock_rounded), title: Text(e.locked ? 'Unlock element' : 'Lock element'), onTap: () { controller.toggleSelectedLock(); Navigator.pop(context); }),
        ListTile(leading: const Icon(Icons.copy_all_outlined), title: const Text('Duplicate element'), onTap: () { controller.duplicateSelected(); Navigator.pop(context); }),
        ListTile(leading: const Icon(Icons.delete_outline_rounded), title: const Text('Delete element'), onTap: () { controller.deleteSelected(); Navigator.pop(context); }),
      ])),
    );
  }

  Future<void> _transformDialog() async {
    final e = controller.selected;
    if (e == null) return;
    final x = TextEditingController(text: e.x.round().toString());
    final y = TextEditingController(text: e.y.round().toString());
    final w = TextEditingController(text: e.width.round().toString());
    final h = TextEditingController(text: e.height.round().toString());
    await showDialog<void>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Transform & Size', style: TextStyle(fontWeight: FontWeight.w900)),
        content: SingleChildScrollView(child: Column(children: [
          Row(children: [Expanded(child: _numberField(x, 'X')), const SizedBox(width: 10), Expanded(child: _numberField(y, 'Y'))]),
          const SizedBox(height: 12),
          Row(children: [Expanded(child: _numberField(w, 'Width')), const SizedBox(width: 10), Expanded(child: _numberField(h, 'Height'))]),
          const SizedBox(height: 8),
          const Text('Use the canvas handles for precise visual resizing.', style: TextStyle(fontSize: 11, color: Colors.black54)),
        ])),
        actions: [TextButton(onPressed: () => Navigator.pop(dialogContext), child: const Text('Cancel')), FilledButton(onPressed: () { controller.updateSelected(x: double.tryParse(x.text), y: double.tryParse(y.text), width: double.tryParse(w.text), height: double.tryParse(h.text)); Navigator.pop(dialogContext); }, child: const Text('Apply'))],
      ),
    );
    x.dispose(); y.dispose(); w.dispose(); h.dispose();
  }

  Widget _numberField(TextEditingController controller, String label) => TextField(controller: controller, keyboardType: const TextInputType.numberWithOptions(decimal: true), decoration: InputDecoration(labelText: label, border: const OutlineInputBorder()));

  Future<void> _replaceImage() async {
    try {
      final result = await _imagePicker.pickImage(source: ImageSource.gallery);
      if (result != null) controller.replaceSelectedImage(await result.readAsBytes());
    } catch (_) {
      _message('Image replace failed.');
    }
  }

  Future<void> _pickImage() async {
    try {
      final result = await _imagePicker.pickImage(source: ImageSource.gallery);
      if (result != null) controller.addImage(await result.readAsBytes());
    } catch (_) {
      _message('Image import failed.');
    }
  }

  Future<void> _showDesignTools() async {
    await showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      builder: (context) => SafeArea(child: Wrap(children: [
        const _SheetHeader(title: 'Design', subtitle: 'Canvas, pages and project-level controls'),
        ListTile(leading: const Icon(Icons.layers_outlined), title: const Text('Pages'), onTap: () { Navigator.pop(context); _showPages(); }),
        ListTile(leading: const Icon(Icons.format_color_fill_outlined), title: const Text('Canvas background'), onTap: () { Navigator.pop(context); _showBackgroundPicker(); }),
        ListTile(leading: const Icon(Icons.aspect_ratio_rounded), title: const Text('Resize canvas'), subtitle: Text('${controller.page.size.width.toInt()} × ${controller.page.size.height.toInt()}'), onTap: () { Navigator.pop(context); _resizeCanvasDialog(); }),
        ListTile(leading: const Icon(Icons.folder_open_outlined), title: const Text('Import image file'), onTap: () { Navigator.pop(context); _pickImageFile(); }),
        if (controller.selected != null) ListTile(leading: const Icon(Icons.auto_fix_high_rounded), title: const Text('Selected element options'), onTap: () { Navigator.pop(context); _showSelectedMore(); }),
      ])),
    );
  }

  Future<void> _resizeCanvasDialog() async {
    final width = TextEditingController(text: controller.page.size.width.round().toString());
    final height = TextEditingController(text: controller.page.size.height.round().toString());
    await showDialog<void>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Resize Canvas', style: TextStyle(fontWeight: FontWeight.w900)),
        content: Row(children: [Expanded(child: _numberField(width, 'Width')), const SizedBox(width: 10), Expanded(child: _numberField(height, 'Height'))]),
        actions: [TextButton(onPressed: () => Navigator.pop(dialogContext), child: const Text('Cancel')), FilledButton(onPressed: () { final w = double.tryParse(width.text); final h = double.tryParse(height.text); if (w != null && h != null) controller.resizeCanvas(w, h); Navigator.pop(dialogContext); }, child: const Text('Resize'))],
      ),
    );
    width.dispose(); height.dispose();
  }

  void _showPages() {
    showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      builder: (context) => SafeArea(child: Padding(padding: const EdgeInsets.fromLTRB(16, 4, 16, 24), child: Column(mainAxisSize: MainAxisSize.min, children: [
        const _SheetHeader(title: 'Pages', subtitle: 'Switch, duplicate or add design pages'),
        ...List.generate(controller.project.pages.length, (index) {
          final p = controller.project.pages[index];
          return ListTile(
            selected: controller.currentPageIndex == index,
            leading: CircleAvatar(backgroundColor: controller.currentPageIndex == index ? _purple : Colors.black12, foregroundColor: controller.currentPageIndex == index ? Colors.white : Colors.black87, child: Text('${index + 1}')),
            title: Text(p.title, style: const TextStyle(fontWeight: FontWeight.w800)),
            subtitle: Text('${p.size.width.toInt()} × ${p.size.height.toInt()}'),
            trailing: controller.currentPageIndex == index ? const Icon(Icons.check_circle_rounded, color: _purple) : null,
            onTap: () { controller.switchPage(index); Navigator.pop(context); },
          );
        }),
        const Divider(height: 20),
        Row(children: [Expanded(child: OutlinedButton.icon(onPressed: () { controller.addPage(); Navigator.pop(context); }, icon: const Icon(Icons.add_rounded), label: const Text('Add Page'))), const SizedBox(width: 10), Expanded(child: OutlinedButton.icon(onPressed: () { controller.duplicatePage(); Navigator.pop(context); }, icon: const Icon(Icons.copy_outlined), label: const Text('Duplicate')))]),
        if (controller.project.pages.length > 1) Padding(padding: const EdgeInsets.only(top: 10), child: OutlinedButton.icon(onPressed: () { controller.deletePage(); Navigator.pop(context); }, icon: const Icon(Icons.delete_outline), label: const Text('Delete current page'))),
      ]))),
    );
  }

  Future<void> _pickImageFile() async {
    try {
      final result = await FilePicker.platform.pickFiles(type: FileType.image, withData: true);
      if (result == null || result.files.isEmpty) return;
      final bytes = result.files.first.bytes;
      if (bytes != null) controller.addImage(bytes);
    } catch (_) {
      _message('Could not import image.');
    }
  }

  void _showBackgroundPicker() {
    const colors = [Colors.white, Color(0xFFF7F8FC), Color(0xFF111827), Color(0xFF0F172A), Color(0xFFEDE9FE), Color(0xFFFEF3C7), Color(0xFFDCFCE7), Color(0xFFFCE7F3), Color(0xFFE0F2FE)];
    showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      builder: (context) => SafeArea(child: Padding(padding: const EdgeInsets.fromLTRB(20, 4, 20, 24), child: Column(mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.start, children: [
        const _SheetHeader(title: 'Canvas Background', subtitle: 'Set the page background color'),
        Wrap(spacing: 14, runSpacing: 14, children: [for (final color in colors) GestureDetector(onTap: () { controller.setBackground(color); Navigator.pop(context); }, child: Container(width: 52, height: 52, decoration: BoxDecoration(color: color, shape: BoxShape.circle, border: Border.all(color: Colors.black12, width: 2))))]),
      ]))),
    );
  }

  Future<void> _handleMenu(String value) async {
    try {
      final width = controller.page.size.width;
      final height = controller.page.size.height;
      switch (value) {
        case 'png':
          final bytes = await _exportService.capturePng(_canvasKey, width, height);
          await _exportService.savePng(bytes, 'naqshkaar_design');
          _message('PNG saved successfully.');
          break;
        case 'jpg':
          final png = await _exportService.capturePng(_canvasKey, width, height);
          await _exportService.saveJpeg(await _exportService.pngToJpeg(png), 'naqshkaar_design');
          _message('JPG saved successfully.');
          break;
        case 'pdf':
          final png = await _exportService.capturePng(_canvasKey, width, height);
          await _exportService.sharePdf(png, width, height, 'naqshkaar_design.pdf');
          break;
      }
    } catch (e) {
      _message('Export failed: $e');
    }
  }

  Future<void> _saveProject() async {
    try {
      await _repository.save(controller.project);
      _message('Project saved successfully.');
    } catch (_) {
      _message('Project save failed.');
    }
  }

  void _message(String text) {
    if (!mounted) return;
    ScaffoldMessenger.of(context)..hideCurrentSnackBar()..showSnackBar(SnackBar(content: Text(text), behavior: SnackBarBehavior.floating));
  }
}

class _SheetHeader extends StatelessWidget {
  final String title;
  final String subtitle;
  const _SheetHeader({required this.title, required this.subtitle});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 5, 20, 12),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(title, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w900)), const SizedBox(height: 3), Text(subtitle, style: const TextStyle(fontSize: 12, color: Colors.black54))]),
    );
  }
}
