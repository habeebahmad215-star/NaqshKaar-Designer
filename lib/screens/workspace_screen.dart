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
  void initState() { super.initState(); controller = WorkspaceController(initial: widget.initialProject, newSize: widget.size); }
  @override
  void dispose() { _viewTransform.dispose(); controller.dispose(); super.dispose(); }

  @override
  Widget build(BuildContext context) => AnimatedBuilder(
    animation: controller,
    builder: (context, _) => Scaffold(
      backgroundColor: _surface,
      appBar: _appBar(),
      body: Column(children: [Expanded(child: _editorArea()), _bottomToolbar()]),
    ),
  );

  PreferredSizeWidget _appBar() => AppBar(
    elevation: 0, backgroundColor: Colors.white, surfaceTintColor: Colors.white, titleSpacing: 2,
    leading: IconButton(tooltip: 'Back', icon: const Icon(Icons.arrow_back_rounded), onPressed: () => Navigator.pop(context)),
    title: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Text(controller.project.name, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w900, color: _ink)),
      Text('Page ${controller.currentPageIndex + 1}  •  ${controller.page.size.width.toInt()} × ${controller.page.size.height.toInt()}', style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w600, color: Colors.black54)),
    ]),
    actions: [
      IconButton(tooltip: 'Save', onPressed: _saveProject, icon: const Icon(Icons.save_outlined)),
      IconButton(tooltip: 'Undo', onPressed: controller.canUndo ? controller.undo : null, icon: const Icon(Icons.undo_rounded)),
      IconButton(tooltip: 'Redo', onPressed: controller.canRedo ? controller.redo : null, icon: const Icon(Icons.redo_rounded)),
      PopupMenuButton<String>(tooltip: 'Export', onSelected: _handleMenu, itemBuilder: (context) => const [
        PopupMenuItem(value: 'png', child: Text('Export PNG')), PopupMenuItem(value: 'jpg', child: Text('Export JPG')), PopupMenuItem(value: 'pdf', child: Text('Share PDF')),
      ]),
    ],
  );

  Widget _editorArea() {
    final page = controller.page;
    return LayoutBuilder(builder: (context, constraints) {
      final width = (constraints.maxWidth - 28).clamp(120.0, double.infinity);
      final height = (constraints.maxHeight - 28).clamp(120.0, double.infinity);
      final baseScale = (width / page.size.width < height / page.size.height ? width / page.size.width : height / page.size.height).clamp(.05, 1.0);
      return AnimatedBuilder(animation: _viewTransform, builder: (context, _) {
        final zoom = _viewTransform.value.getMaxScaleOnAxis().clamp(.5, 4.0);
        return Padding(padding: const EdgeInsets.all(14), child: Stack(children: [
          Positioned.fill(child: InteractiveViewer(
            transformationController: _viewTransform, minScale: .5, maxScale: 4, constrained: false, boundaryMargin: const EdgeInsets.all(220),
            child: Center(child: SizedBox(width: width, height: height, child: FittedBox(
              fit: BoxFit.contain, alignment: Alignment.center,
              child: DesignCanvas(controller: controller, repaintKey: _canvasKey, interactionScale: baseScale * zoom),
            ))),
          )),
          Positioned(top: 8, right: 8, child: _floatingButton(Icons.center_focus_strong_rounded, 'Reset zoom', () => _viewTransform.value = Matrix4.identity())),
          Positioned(left: 8, bottom: 8, child: _zoomBadge(zoom)),
        ]));
      });
    });
  }

  Widget _floatingButton(IconData icon, String tooltip, VoidCallback onTap) => Material(
    color: Colors.white, elevation: 3, shadowColor: Colors.black26, borderRadius: BorderRadius.circular(13),
    child: IconButton(tooltip: tooltip, onPressed: onTap, icon: Icon(icon, size: 21)),
  );
  Widget _zoomBadge(double zoom) => Material(color: Colors.white, elevation: 2, borderRadius: BorderRadius.circular(18), child: Padding(
    padding: const EdgeInsets.symmetric(horizontal: 11, vertical: 7), child: Text('${(zoom * 100).round()}%', style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800)),
  ));

  Widget _bottomToolbar() {
    final selected = controller.selected;
    return SafeArea(top: false, child: Container(
      decoration: const BoxDecoration(color: Colors.white, boxShadow: [BoxShadow(blurRadius: 18, offset: Offset(0, -5), color: Color(0x1A000000))]),
      padding: const EdgeInsets.fromLTRB(10, 7, 10, 8), child: selected == null ? _mainTools() : _contextualTools(selected),
    ));
  }

  Widget _mainTools() => Row(children: [
    _primaryTool(Icons.text_fields_rounded, 'Text', _addText),
    _primaryTool(Icons.crop_square_rounded, 'Shape', () => controller.addShape()),
    _primaryTool(Icons.image_outlined, 'Image', _pickImage),
    _primaryTool(Icons.layers_outlined, 'Pages', _showPages),
    _primaryTool(Icons.tune_rounded, 'Design', _showDesignTools),
  ]);

  Widget _contextualTools(DesignElement e) {
    final isText = e.kind == ElementKind.text, isShape = e.kind == ElementKind.shape;
    return Column(mainAxisSize: MainAxisSize.min, children: [
      SizedBox(height: 58, child: ListView(scrollDirection: Axis.horizontal, children: [
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
      ])),
      const SizedBox(height: 2),
      Row(children: [Expanded(child: Row(children: [Container(width: 8, height: 8, decoration: const BoxDecoration(color: _purple, shape: BoxShape.circle)), const SizedBox(width: 7), Expanded(child: Text(_selectionLabel(e), maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800)))])),
        _quickIcon(Icons.copy_outlined, 'Duplicate', controller.duplicateSelected),
        _quickIcon(e.locked ? Icons.lock_rounded : Icons.lock_open_rounded, e.locked ? 'Unlock' : 'Lock', controller.toggleSelectedLock),
        _quickIcon(Icons.delete_outline_rounded, 'Delete', controller.deleteSelected),
      ]),
    ]);
  }

  String _selectionLabel(DesignElement e) {
    if (e.kind == ElementKind.text) return 'Urdu Text  •  ${e.fontFamily == 'JameelNoori' ? 'Gulzar' : e.fontFamily}';
    if (e.kind == ElementKind.image) return 'Image  •  ${e.width.toInt()} × ${e.height.toInt()}';
    return 'Shape  •  ${e.width.toInt()} × ${e.height.toInt()}';
  }

  Widget _primaryTool(IconData icon, String label, VoidCallback onTap) => Expanded(child: InkWell(
    onTap: onTap, borderRadius: BorderRadius.circular(14), child: Padding(padding: const EdgeInsets.symmetric(vertical: 5), child: Column(children: [Icon(icon, size: 25, color: _purple), const SizedBox(height: 4), Text(label, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800))])),
  ));
  Widget _contextTool(IconData icon, String label, VoidCallback onTap) => Padding(padding: const EdgeInsets.symmetric(horizontal: 3), child: InkWell(
    onTap: onTap, borderRadius: BorderRadius.circular(12), child: SizedBox(width: 62, child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [Icon(icon, size: 21, color: _purple), const SizedBox(height: 3), Text(label, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 9, fontWeight: FontWeight.w800))])),
  ));
  Widget _toggleTool(IconData icon, String label, bool active, VoidCallback onTap) => Padding(padding: const EdgeInsets.symmetric(horizontal: 3), child: InkWell(
    onTap: onTap, borderRadius: BorderRadius.circular(12), child: Container(width: 62, decoration: BoxDecoration(color: active ? _purple.withValues(alpha: .10) : Colors.transparent, borderRadius: BorderRadius.circular(12)), child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [Icon(icon, size: 21, color: active ? _purple : Colors.black54), const SizedBox(height: 3), Text(label, style: TextStyle(fontSize: 9, fontWeight: FontWeight.w800, color: active ? _purple : Colors.black87))])),
  ));
  Widget _quickIcon(IconData icon, String tooltip, VoidCallback onTap) => IconButton(tooltip: tooltip, visualDensity: VisualDensity.compact, onPressed: onTap, icon: Icon(icon, size: 21));

  Future<void> _addText() async { final text = await _textDialog(initial: 'اپنا متن یہاں لکھیں'); if (text != null && text.trim().isNotEmpty) controller.addText(text: text.trim()); }
  Future<void> _editText() async { final e = controller.selected; if (e == null) return; final text = await _textDialog(initial: e.text); if (text != null) controller.editSelectedText(text); }
  Future<String?> _textDialog({required String initial}) async {
    final c = TextEditingController(text: initial);
    final result = await showDialog<String>(context: context, builder: (dialogContext) => AlertDialog(
      title: const Text('Urdu Text', style: TextStyle(fontWeight: FontWeight.w900)),
      content: TextField(controller: c, autofocus: true, maxLines: 7, textDirection: TextDirection.rtl, style: const TextStyle(fontFamily: 'Gulzar', fontSize: 23), decoration: const InputDecoration(hintText: 'اپنا متن یہاں لکھیں', border: OutlineInputBorder())),
      actions: [TextButton(onPressed: () => Navigator.pop(dialogContext), child: const Text('Cancel')), FilledButton(onPressed: () => Navigator.pop(dialogContext, c.text), child: const Text('Apply'))],
    ));
    c.dispose(); return result;
  }

  Future<void> _fontDialog() async {
    final e = controller.selected; if (e == null) return;
    final result = await showModalBottomSheet<String>(context: context, showDragHandle: true, builder: (context) => SafeArea(child: ListView(shrinkWrap: true, children: [
      const _SheetHeader(title: 'Urdu Fonts', subtitle: 'Choose a Nastaliq family'),
      _fontTile('Gulzar', 'Contemporary Nastaliq', 'Gulzar', e.fontFamily), _fontTile('Noto Nastaliq Urdu', 'Google Fonts Nastaliq', 'NotoNastaliqUrdu', e.fontFamily),
    ])));
    if (result != null) controller.setSelectedFont(result);
  }
  Widget _fontTile(String title, String subtitle, String family, String current) {
    final selected = current == family || (current == 'JameelNoori' && family == 'Gulzar');
    return ListTile(leading: CircleAvatar(backgroundColor: selected ? _purple : Colors.black12, child: Icon(Icons.font_download_rounded, color: selected ? Colors.white : Colors.black54)), title: Text(title, style: TextStyle(fontFamily: family, fontSize: 22, fontWeight: FontWeight.w700)), subtitle: Text(subtitle), trailing: selected ? const Icon(Icons.check_circle_rounded, color: _purple) : null, onTap: () => Navigator.pop(context, family));
  }
  Future<void> _fontSizeDialog(DesignElement e) async {
    double value = e.fontSize;
    final result = await showDialog<double>(context: context, builder: (dialogContext) => StatefulBuilder(builder: (context, setState) => AlertDialog(
      title: const Text('Font Size', style: TextStyle(fontWeight: FontWeight.w900)), content: Column(mainAxisSize: MainAxisSize.min, children: [Text('${value.round()} px', style: const TextStyle(fontSize: 26, fontWeight: FontWeight.w900, color: _purple)), Slider(min: 8, max: 300, divisions: 73, value: value.clamp(8, 300), onChanged: (v) => setState(() => value = v))]),
      actions: [TextButton(onPressed: () => Navigator.pop(dialogContext), child: const Text('Cancel')), FilledButton(onPressed: () => Navigator.pop(dialogContext, value), child: const Text('Apply'))],
    )));
    if (result != null) controller.setSelectedFontSize(result);
  }
  Future<void> _colorDialog() async {
    final e = controller.selected; if (e == null) return;
    final colors = [Colors.black, Colors.white, _purple, const Color(0xFF0F766E), const Color(0xFFDC2626), const Color(0xFFF59E0B), const Color(0xFF2563EB)];
    final result = await showModalBottomSheet<Color>(context: context, showDragHandle: true, builder: (context) => SafeArea(child: Padding(padding: const EdgeInsets.all(18), child: Wrap(spacing: 14, runSpacing: 14, children: colors.map((c) => InkWell(onTap: () => Navigator.pop(context, c), borderRadius: BorderRadius.circular(30), child: CircleAvatar(backgroundColor: c, radius: 25, child: c.toARGB32() == e.colorValue ? const Icon(Icons.check, color: Colors.white) : null))).toList()))));
    if (result != null) controller.updateSelected(colorValue: result.toARGB32());
  }
  Future<void> _opacityDialog() async {
    final e = controller.selected; if (e == null) return; double value = e.opacity;
    final result = await showDialog<double>(context: context, builder: (dialogContext) => StatefulBuilder(builder: (context, setState) => AlertDialog(title: const Text('Opacity', style: TextStyle(fontWeight: FontWeight.w900)), content: Column(mainAxisSize: MainAxisSize.min, children: [Text('${(value * 100).round()}%', style: const TextStyle(fontSize: 26, fontWeight: FontWeight.w900, color: _purple)), Slider(value: value, min: 0, max: 1, divisions: 20, onChanged: (v) => setState(() => value = v))]), actions: [TextButton(onPressed: () => Navigator.pop(dialogContext), child: const Text('Cancel')), FilledButton(onPressed: () => Navigator.pop(dialogContext, value), child: const Text('Apply'))])));
    if (result != null) controller.setSelectedOpacity(result);
  }
  Future<void> _radiusDialog() async {
    final e = controller.selected; if (e == null || e.kind != ElementKind.shape) return; double value = e.radius;
    final result = await showDialog<double>(context: context, builder: (dialogContext) => StatefulBuilder(builder: (context, setState) => AlertDialog(title: const Text('Corner Radius', style: TextStyle(fontWeight: FontWeight.w900)), content: Slider(value: value.clamp(0, 240), min: 0, max: 240, divisions: 24, onChanged: (v) => setState(() => value = v)), actions: [TextButton(onPressed: () => Navigator.pop(dialogContext), child: const Text('Cancel')), FilledButton(onPressed: () => Navigator.pop(dialogContext, value), child: const Text('Apply'))])));
    if (result != null) controller.setSelectedRadius(result);
  }
  Future<void> _alignmentDialog() async {
    final e = controller.selected; if (e == null || e.kind != ElementKind.text) return;
    final result = await showModalBottomSheet<TextAlign>(context: context, showDragHandle: true, builder: (context) => SafeArea(child: Column(mainAxisSize: MainAxisSize.min, children: [const _SheetHeader(title: 'Text Alignment', subtitle: 'Set the text inside its frame'), for (final item in const [(TextAlign.right, 'Right', Icons.format_align_right_rounded), (TextAlign.center, 'Center', Icons.format_align_center_rounded), (TextAlign.left, 'Left', Icons.format_align_left_rounded), (TextAlign.justify, 'Justify', Icons.format_align_justify_rounded)]) ListTile(leading: Icon(item.$3), title: Text(item.$2), onTap: () => Navigator.pop(context, item.$1))])));
    if (result != null) controller.setSelectedAlign(result);
  }
  Future<void> _directionDialog() async {
    final e = controller.selected; if (e == null || e.kind != ElementKind.text) return;
    final result = await showModalBottomSheet<TextDirection>(context: context, showDragHandle: true, builder: (context) => SafeArea(child: Column(mainAxisSize: MainAxisSize.min, children: [const _SheetHeader(title: 'Text Direction', subtitle: 'Control RTL / LTR layout'), ListTile(leading: const Icon(Icons.format_textdirection_r_to_l), title: const Text('Right to Left (Urdu)'), onTap: () => Navigator.pop(context, TextDirection.rtl)), ListTile(leading: const Icon(Icons.format_textdirection_l_to_r), title: const Text('Left to Right'), onTap: () => Navigator.pop(context, TextDirection.ltr))])));
    if (result != null) controller.setSelectedDirection(result);
  }
  Future<void> _arrangeDialog() async {
    final e = controller.selected; if (e == null) return;
    await showModalBottomSheet<void>(context: context, showDragHandle: true, builder: (context) => SafeArea(child: Column(mainAxisSize: MainAxisSize.min, children: [const _SheetHeader(title: 'Arrange', subtitle: 'Control layer order and placement'), ListTile(leading: const Icon(Icons.vertical_align_top_rounded), title: const Text('Bring to front'), onTap: () { controller.bringSelectedToFront(); Navigator.pop(context); }), ListTile(leading: const Icon(Icons.vertical_align_bottom_rounded), title: const Text('Send to back'), onTap: () { controller.sendSelectedToBack(); Navigator.pop(context); }), ListTile(leading: const Icon(Icons.center_focus_strong_rounded), title: const Text('Center on page'), onTap: () { controller.centerSelected(); Navigator.pop(context); })])));
  }
  Future<void> _showSelectedMore() async {
    final e = controller.selected; if (e == null) return;
    await showModalBottomSheet<void>(context: context, showDragHandle: true, builder: (context) => SafeArea(child: Column(mainAxisSize: MainAxisSize.min, children: [const _SheetHeader(title: 'More options', subtitle: 'Advanced controls for this element'), ListTile(leading: const Icon(Icons.copy_outlined), title: const Text('Duplicate'), onTap: () { controller.duplicateSelected(); Navigator.pop(context); }), ListTile(leading: const Icon(Icons.flip_to_front_rounded), title: const Text('Bring to front'), onTap: () { controller.bringSelectedToFront(); Navigator.pop(context); }), ListTile(leading: const Icon(Icons.flip_to_back_rounded), title: const Text('Send to back'), onTap: () { controller.sendSelectedToBack(); Navigator.pop(context); }), ListTile(leading: Icon(e.hidden ? Icons.visibility_rounded : Icons.visibility_off_rounded), title: Text(e.hidden ? 'Show element' : 'Hide element'), onTap: () { controller.toggleSelectedHidden(); Navigator.pop(context); }), ListTile(leading: const Icon(Icons.rotate_0_degrees_ccw_rounded), title: const Text('Reset rotation'), onTap: () { controller.resetSelectedRotation(); Navigator.pop(context); })])));
  }
  Future<void> _showDesignTools() async {
    await showModalBottomSheet<void>(context: context, showDragHandle: true, builder: (context) => SafeArea(child: Column(mainAxisSize: MainAxisSize.min, children: [const _SheetHeader(title: 'Design', subtitle: 'Page-level tools'), ListTile(leading: const Icon(Icons.layers_outlined), title: const Text('Pages'), onTap: () { Navigator.pop(context); _showPages(); }), ListTile(leading: const Icon(Icons.wallpaper_outlined), title: const Text('Background'), onTap: () { Navigator.pop(context); _backgroundDialog(); }), ListTile(leading: const Icon(Icons.photo_size_select_large_outlined), title: const Text('Canvas size'), onTap: () { Navigator.pop(context); _canvasSizeDialog(); })])));
  }
  Future<void> _backgroundDialog() async {
    final colors = [Colors.white, const Color(0xFFF8FAFC), const Color(0xFF111827), const Color(0xFF1E1B4B), const Color(0xFFFEF3C7), const Color(0xFFE0F2FE)];
    final result = await showModalBottomSheet<Color>(context: context, showDragHandle: true, builder: (context) => SafeArea(child: Padding(padding: const EdgeInsets.all(18), child: Wrap(spacing: 14, runSpacing: 14, children: colors.map((c) => InkWell(onTap: () => Navigator.pop(context, c), child: CircleAvatar(backgroundColor: c, radius: 25))).toList()))));
    if (result != null) controller.setBackground(result);
  }
  Future<void> _canvasSizeDialog() async {
    final w = TextEditingController(text: controller.page.size.width.toInt().toString()), h = TextEditingController(text: controller.page.size.height.toInt().toString());
    final result = await showDialog<List<double>>(context: context, builder: (dialogContext) => AlertDialog(title: const Text('Canvas Size', style: TextStyle(fontWeight: FontWeight.w900)), content: Row(children: [Expanded(child: TextField(controller: w, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Width'))), const SizedBox(width: 12), Expanded(child: TextField(controller: h, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Height')))]), actions: [TextButton(onPressed: () => Navigator.pop(dialogContext), child: const Text('Cancel')), FilledButton(onPressed: () { final width = double.tryParse(w.text), height = double.tryParse(h.text); if (width != null && height != null) Navigator.pop(dialogContext, [width, height]); }, child: const Text('Apply'))]));
    w.dispose(); h.dispose(); if (result != null) controller.resizeCanvas(result[0], result[1]);
  }
  Future<void> _pickImage() async { final result = await _imagePicker.pickImage(source: ImageSource.gallery, imageQuality: 95); if (result == null) return; controller.addImage(await result.readAsBytes()); }
  Future<void> _saveProject() async { await _repository.save(controller.project); if (!mounted) return; ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Project saved'))); }
  Future<void> _handleMenu(String value) async { try { if (value == 'png') await _exportService.exportPng(controller.page, _canvasKey); if (value == 'jpg') await _exportService.exportJpg(controller.page, _canvasKey); if (value == 'pdf') await _exportService.sharePdf(controller.project); if (!mounted) return; ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(value == 'pdf' ? 'PDF ready to share' : 'Export complete'))); } catch (e) { if (!mounted) return; ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Export failed: $e'))); } }
  Future<void> _showPages() async { await showModalBottomSheet<void>(context: context, showDragHandle: true, builder: (context) => SafeArea(child: Column(mainAxisSize: MainAxisSize.min, children: [const _SheetHeader(title: 'Pages', subtitle: 'Manage multi-page designs'), for (var i = 0; i < controller.project.pages.length; i++) ListTile(leading: CircleAvatar(child: Text('${i + 1}')), title: Text(controller.project.pages[i].title), selected: i == controller.currentPageIndex, onTap: () { controller.switchPage(i); Navigator.pop(context); }), const Divider(), Row(mainAxisAlignment: MainAxisAlignment.spaceEvenly, children: [TextButton.icon(onPressed: () { controller.addPage(); Navigator.pop(context); }, icon: const Icon(Icons.add), label: const Text('Add page')), TextButton.icon(onPressed: () { controller.duplicatePage(); Navigator.pop(context); }, icon: const Icon(Icons.copy), label: const Text('Duplicate')), TextButton.icon(onPressed: controller.project.pages.length > 1 ? () { controller.deletePage(); Navigator.pop(context); } : null, icon: const Icon(Icons.delete_outline), label: const Text('Delete'))])]))); }
}

class _SheetHeader extends StatelessWidget {
  final String title, subtitle;
  const _SheetHeader({required this.title, required this.subtitle});
  @override
  Widget build(BuildContext context) => Padding(padding: const EdgeInsets.fromLTRB(20, 6, 20, 8), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(title, style: const TextStyle(fontSize: 19, fontWeight: FontWeight.w900)), const SizedBox(height: 3), Text(subtitle, style: const TextStyle(fontSize: 12, color: Colors.black54))]));
}