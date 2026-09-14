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
  final ExportService _export = ExportService();
  final ProjectRepository _repo = ProjectRepository();
  final ImagePicker _picker = ImagePicker();
  final TransformationController _transform = TransformationController();
  static const _primary = Color(0xFF6D28D9);
  static const _ink = Color(0xFF171326);
  static const _bg = Color(0xFFF5F3F9);

  @override
  void initState() { super.initState(); controller = WorkspaceController(initial: widget.initialProject, newSize: widget.size); }
  @override
  void dispose() { _transform.dispose(); controller.dispose(); super.dispose(); }

  @override
  Widget build(BuildContext context) => AnimatedBuilder(
    animation: controller,
    builder: (_, __) => Scaffold(backgroundColor: _bg, appBar: _appBar(), body: Column(children: [Expanded(child: _canvasArea()), _toolbar()])),
  );

  PreferredSizeWidget _appBar() => AppBar(
    backgroundColor: Colors.white, surfaceTintColor: Colors.white, elevation: 0,
    leading: IconButton(icon: const Icon(Icons.arrow_back_rounded), onPressed: () => Navigator.pop(context)),
    titleSpacing: 0,
    title: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Text(controller.project.name, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w900, color: _ink)),
      Text('Page ${controller.currentPageIndex + 1}  •  ${controller.page.size.width.round()} × ${controller.page.size.height.round()}', style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w600, color: Colors.black54)),
    ]),
    actions: [
      IconButton(tooltip: 'Undo', onPressed: controller.canUndo ? controller.undo : null, icon: const Icon(Icons.undo_rounded)),
      IconButton(tooltip: 'Redo', onPressed: controller.canRedo ? controller.redo : null, icon: const Icon(Icons.redo_rounded)),
      IconButton(tooltip: 'Save', onPressed: _save, icon: const Icon(Icons.save_outlined)),
      PopupMenuButton<String>(onSelected: _exportMenu, itemBuilder: (_) => const [PopupMenuItem(value: 'png', child: Text('Export PNG')), PopupMenuItem(value: 'jpg', child: Text('Export JPG')), PopupMenuItem(value: 'pdf', child: Text('Share PDF'))]),
    ],
  );

  Widget _canvasArea() => LayoutBuilder(builder: (context, c) {
    final maxW = (c.maxWidth - 28).clamp(120.0, double.infinity);
    final maxH = (c.maxHeight - 28).clamp(120.0, double.infinity);
    final fitScale = (maxW / controller.page.size.width < maxH / controller.page.size.height ? maxW / controller.page.size.width : maxH / controller.page.size.height).clamp(.05, 1.0);
    return AnimatedBuilder(animation: _transform, builder: (_, __) {
      final zoom = _transform.value.getMaxScaleOnAxis().clamp(.5, 4.0);
      return Padding(padding: const EdgeInsets.all(14), child: Stack(children: [
        Positioned.fill(child: InteractiveViewer(transformationController: _transform, minScale: .5, maxScale: 4, constrained: false, boundaryMargin: const EdgeInsets.all(240), child: Center(child: SizedBox(width: maxW, height: maxH, child: FittedBox(fit: BoxFit.contain, child: DesignCanvas(controller: controller, repaintKey: _canvasKey, interactionScale: fitScale * zoom))))),
        Positioned(top: 8, right: 8, child: _roundButton(Icons.center_focus_strong_rounded, 'Reset view', () => _transform.value = Matrix4.identity())),
        Positioned(left: 8, bottom: 8, child: _badge('${(zoom * 100).round()}%')),
      ]));
    });
  });

  Widget _roundButton(IconData icon, String tip, VoidCallback tap) => Material(color: Colors.white, elevation: 3, borderRadius: BorderRadius.circular(14), child: IconButton(tooltip: tip, onPressed: tap, icon: Icon(icon, size: 21)));
  Widget _badge(String text) => Material(color: Colors.white, elevation: 2, borderRadius: BorderRadius.circular(18), child: Padding(padding: const EdgeInsets.symmetric(horizontal: 11, vertical: 7), child: Text(text, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800))));

  Widget _toolbar() => SafeArea(top: false, child: Container(decoration: const BoxDecoration(color: Colors.white, boxShadow: [BoxShadow(blurRadius: 20, offset: Offset(0, -5), color: Color(0x18000000))]), padding: const EdgeInsets.fromLTRB(9, 7, 9, 8), child: controller.selected == null ? _mainTools() : _selectedTools(controller.selected!)));
  Widget _mainTools() => Row(children: [_mainTool(Icons.text_fields_rounded, 'Text', _addText), _mainTool(Icons.crop_square_rounded, 'Shape', controller.addShape), _mainTool(Icons.image_outlined, 'Image', _pickImage), _mainTool(Icons.layers_outlined, 'Pages', _pagesSheet), _mainTool(Icons.tune_rounded, 'Design', _designSheet)]);

  Widget _selectedTools(DesignElement e) {
    final text = e.kind == ElementKind.text;
    final shape = e.kind == ElementKind.shape;
    final tools = <Widget>[
      if (text) _tool(Icons.edit_rounded, 'Edit', _editText),
      if (text) _tool(Icons.font_download_outlined, 'Font', _fontSheet),
      if (text) _tool(Icons.format_size_rounded, '${e.fontSize.round()}', () => _fontSize(e)),
      if (text) _toggle(Icons.format_bold_rounded, 'Bold', e.bold, controller.toggleSelectedBold),
      if (text) _toggle(Icons.format_italic_rounded, 'Italic', e.italic, controller.toggleSelectedItalic),
      _tool(Icons.palette_outlined, 'Color', _colorSheet),
      _tool(Icons.auto_awesome_rounded, 'Effects', _effectsSheet),
      if (text) _tool(Icons.format_line_spacing_rounded, 'Spacing', _spacingSheet),
      if (shape) _tool(Icons.rounded_corner, 'Corners', _radius),
      _tool(Icons.opacity_rounded, 'Opacity', _opacity),
      if (text) _tool(Icons.format_align_center_rounded, 'Align', _alignSheet),
      if (text) _tool(Icons.translate_rounded, 'RTL/LTR', _directionSheet),
      _tool(Icons.open_with_rounded, 'Arrange', _arrangeSheet),
      _tool(Icons.more_horiz_rounded, 'More', _moreSheet),
    ];
    return Column(mainAxisSize: MainAxisSize.min, children: [SizedBox(height: 60, child: ListView(scrollDirection: Axis.horizontal, children: tools)), Row(children: [Expanded(child: Row(children: [Container(width: 8, height: 8, decoration: const BoxDecoration(color: _primary, shape: BoxShape.circle)), const SizedBox(width: 7), Expanded(child: Text(_label(e), maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800)))])), IconButton(tooltip: 'Duplicate', visualDensity: VisualDensity.compact, onPressed: controller.duplicateSelected, icon: const Icon(Icons.copy_outlined)), IconButton(tooltip: e.locked ? 'Unlock' : 'Lock', visualDensity: VisualDensity.compact, onPressed: controller.toggleSelectedLock, icon: Icon(e.locked ? Icons.lock_rounded : Icons.lock_open_rounded)), IconButton(tooltip: 'Delete', visualDensity: VisualDensity.compact, onPressed: controller.deleteSelected, icon: const Icon(Icons.delete_outline_rounded))])]);
  }

  String _label(DesignElement e) { if (e.kind == ElementKind.text) return 'Urdu Text  •  ${e.fontFamily == 'JameelNoori' ? 'Gulzar' : e.fontFamily}'; if (e.kind == ElementKind.image) return 'Image  •  ${e.width.round()} × ${e.height.round()}'; return 'Shape  •  ${e.width.round()} × ${e.height.round()}'; }
  Widget _mainTool(IconData icon, String label, VoidCallback tap) => Expanded(child: InkWell(onTap: tap, borderRadius: BorderRadius.circular(14), child: Padding(padding: const EdgeInsets.symmetric(vertical: 5), child: Column(children: [Icon(icon, color: _primary, size: 25), const SizedBox(height: 4), Text(label, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800))]))));
  Widget _tool(IconData icon, String label, VoidCallback tap) => Padding(padding: const EdgeInsets.symmetric(horizontal: 3), child: InkWell(onTap: tap, borderRadius: BorderRadius.circular(12), child: SizedBox(width: 64, child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [Icon(icon, color: _primary, size: 21), const SizedBox(height: 3), Text(label, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 9, fontWeight: FontWeight.w800))]))));
  Widget _toggle(IconData icon, String label, bool active, VoidCallback tap) => Padding(padding: const EdgeInsets.symmetric(horizontal: 3), child: InkWell(onTap: tap, borderRadius: BorderRadius.circular(12), child: Container(width: 64, decoration: BoxDecoration(color: active ? _primary.withValues(alpha: .10) : Colors.transparent, borderRadius: BorderRadius.circular(12)), child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [Icon(icon, color: active ? _primary : Colors.black54, size: 21), const SizedBox(height: 3), Text(label, style: TextStyle(fontSize: 9, fontWeight: FontWeight.w800, color: active ? _primary : Colors.black87))]))));

  Future<void> _addText() async { final value = await _textDialog('Add Urdu Text', 'اپنا متن یہاں لکھیں'); if (value != null && value.trim().isNotEmpty) controller.addText(text: value.trim()); }
  Future<void> _editText() async { final e = controller.selected; if (e == null) return; final value = await _textDialog('Edit Text', e.text); if (value != null) controller.editSelectedText(value); }
  Future<String?> _textDialog(String title, String initial) async { final c = TextEditingController(text: initial); final result = await showDialog<String>(context: context, builder: (d) => AlertDialog(title: Text(title, style: const TextStyle(fontWeight: FontWeight.w900)), content: TextField(controller: c, autofocus: true, maxLines: 7, textDirection: TextDirection.rtl, style: const TextStyle(fontFamily: 'Gulzar', fontSize: 23), decoration: const InputDecoration(hintText: 'اردو متن', border: OutlineInputBorder())), actions: [TextButton(onPressed: () => Navigator.pop(d), child: const Text('Cancel')), FilledButton(onPressed: () => Navigator.pop(d, c.text), child: const Text('Apply'))])); c.dispose(); return result; }

  Future<void> _fontSheet() async { final e = controller.selected; if (e == null) return; final family = await showModalBottomSheet<String>(context: context, showDragHandle: true, builder: (_) => SafeArea(child: ListView(shrinkWrap: true, children: [const _Header('Urdu Typography', 'Premium Nastaliq font families'), _fontTile('Gulzar', 'Contemporary Nastaliq', 'Gulzar', e.fontFamily), _fontTile('Noto Nastaliq Urdu', 'Google Fonts Nastaliq', 'NotoNastaliqUrdu', e.fontFamily)]))); if (family != null) controller.setSelectedFont(family); }
  Widget _fontTile(String title, String sub, String family, String current) { final active = current == family || (current == 'JameelNoori' && family == 'Gulzar'); return ListTile(leading: CircleAvatar(backgroundColor: active ? _primary : Colors.black12, child: Icon(Icons.font_download_rounded, color: active ? Colors.white : Colors.black54)), title: Text(title, style: TextStyle(fontFamily: family, fontSize: 21, fontWeight: FontWeight.w700)), subtitle: Text(sub), trailing: active ? const Icon(Icons.check_circle_rounded, color: _primary) : null, onTap: () => Navigator.pop(context, family)); }
  Future<void> _fontSize(DesignElement e) async { await _sliderSheet('Font Size', e.fontSize, 8, 300, (v) => '${v.round()} px', controller.setSelectedFontSize); }
  Future<void> _opacity() async { final e = controller.selected; if (e == null) return; await _sliderSheet('Opacity', e.opacity, 0, 1, (v) => '${(v * 100).round()}%', controller.setSelectedOpacity, divisions: 20); }
  Future<void> _radius() async { final e = controller.selected; if (e == null) return; await _sliderSheet('Corner Radius', e.radius, 0, 240, (v) => '${v.round()} px', controller.setSelectedRadius); }

  Future<void> _effectsSheet() async { final e = controller.selected; if (e == null) return; await showModalBottomSheet<void>(context: context, isScrollControlled: true, showDragHandle: true, builder: (_) => _EffectsPanel(controller: controller, element: e)); }
  Future<void> _spacingSheet() async { final e = controller.selected; if (e == null) return; double letter = e.letterSpacing, line = e.lineHeight; await showModalBottomSheet<void>(context: context, showDragHandle: true, builder: (sheet) => StatefulBuilder(builder: (_, set) => SafeArea(child: Padding(padding: const EdgeInsets.fromLTRB(20, 4, 20, 20), child: Column(mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.start, children: [const _Header('Typography Spacing', 'Fine control for Nastaliq composition'), Text('Letter spacing  ${letter.toStringAsFixed(1)}'), Slider(min: -10, max: 20, divisions: 60, value: letter, onChanged: (v) => set(() => letter = v)), Text('Line height  ${line.toStringAsFixed(2)}×'), Slider(min: .7, max: 3, divisions: 46, value: line, onChanged: (v) => set(() => line = v)), SizedBox(width: double.infinity, child: FilledButton.icon(onPressed: () { controller.setSelectedTypography(letterSpacing: letter, lineHeight: line); Navigator.pop(sheet); }, icon: const Icon(Icons.check_rounded), label: const Text('Apply typography')))])))); }
  Future<void> _colorSheet() async { final e = controller.selected; if (e == null) return; final colors = [Colors.black, Colors.white, _primary, const Color(0xFF0F766E), const Color(0xFFDC2626), const Color(0xFFF59E0B), const Color(0xFF2563EB), const Color(0xFF7C2D12), const Color(0xFFDB2777)]; final color = await showModalBottomSheet<Color>(context: context, showDragHandle: true, builder: (_) => SafeArea(child: Padding(padding: const EdgeInsets.all(20), child: Wrap(spacing: 14, runSpacing: 14, children: colors.map((c) => InkWell(onTap: () => Navigator.pop(context, c), child: CircleAvatar(radius: 25, backgroundColor: c, child: c.toARGB32() == e.colorValue ? const Icon(Icons.check, color: Colors.white) : null))).toList())))); if (color != null) controller.updateSelected(colorValue: color.toARGB32()); }
  Future<void> _alignSheet() async { final e = controller.selected; if (e == null) return; final a = await _choiceSheet<TextAlign>('Text Alignment', [TextAlign.left, TextAlign.center, TextAlign.right, TextAlign.justify], (x) => x.name); if (a != null) controller.setSelectedAlign(a); }
  Future<void> _directionSheet() async { final d = await _choiceSheet<TextDirection>('Text Direction', [TextDirection.rtl, TextDirection.ltr], (x) => x == TextDirection.rtl ? 'Right to left (Urdu)' : 'Left to right'); if (d != null) controller.setSelectedDirection(d); }
  Future<T?> _choiceSheet<T>(String title, List<T> values, String Function(T) label) => showModalBottomSheet<T>(context: context, showDragHandle: true, builder: (_) => SafeArea(child: ListView(shrinkWrap: true, children: [_Header(title, 'Choose a professional layout setting'), ...values.map((v) => ListTile(title: Text(label(v), style: const TextStyle(fontWeight: FontWeight.w700)), onTap: () => Navigator.pop(context, v)))])));
  Future<void> _arrangeSheet() async { await showModalBottomSheet<void>(context: context, showDragHandle: true, builder: (_) => SafeArea(child: Wrap(children: [const _Header('Arrange', 'Precise layer and position controls'), ListTile(leading: const Icon(Icons.vertical_align_top_rounded), title: const Text('Bring to front'), onTap: () { controller.bringSelectedToFront(); Navigator.pop(context); }), ListTile(leading: const Icon(Icons.vertical_align_bottom_rounded), title: const Text('Send to back'), onTap: () { controller.sendSelectedToBack(); Navigator.pop(context); }), ListTile(leading: const Icon(Icons.center_focus_strong_rounded), title: const Text('Center on canvas'), onTap: () { controller.centerSelected(); Navigator.pop(context); })]))); }
  Future<void> _moreSheet() async { await showModalBottomSheet<void>(context: context, showDragHandle: true, builder: (_) => SafeArea(child: Wrap(children: [const _Header('Object', 'More professional editing actions'), ListTile(leading: const Icon(Icons.copy_rounded), title: const Text('Duplicate'), onTap: () { controller.duplicateSelected(); Navigator.pop(context); }), ListTile(leading: const Icon(Icons.visibility_off_outlined), title: const Text('Hide / Show'), onTap: () { controller.toggleSelectedHidden(); Navigator.pop(context); }), ListTile(leading: const Icon(Icons.rotate_left_rounded), title: const Text('Reset rotation'), onTap: () { controller.resetSelectedRotation(); Navigator.pop(context); }), ListTile(leading: const Icon(Icons.delete_outline_rounded), title: const Text('Delete', style: TextStyle(color: Colors.red)), onTap: () { controller.deleteSelected(); Navigator.pop(context); })]))); }
  Future<void> _sliderSheet(String title, double initial, double min, double max, String Function(double) display, ValueChanged<double> apply, {int? divisions}) async { double value = initial.clamp(min, max); await showModalBottomSheet<void>(context: context, showDragHandle: true, builder: (sheet) => StatefulBuilder(builder: (_, set) => SafeArea(child: Padding(padding: const EdgeInsets.fromLTRB(20, 4, 20, 24), child: Column(mainAxisSize: MainAxisSize.min, children: [Text(title, style: const TextStyle(fontSize: 19, fontWeight: FontWeight.w900)), const SizedBox(height: 10), Text(display(value), style: const TextStyle(fontSize: 27, fontWeight: FontWeight.w900, color: _primary)), Slider(min: min, max: max, divisions: divisions, value: value, onChanged: (v) => set(() => value = v)), FilledButton.icon(onPressed: () { apply(value); Navigator.pop(sheet); }, icon: const Icon(Icons.check_rounded), label: const Text('Apply'))])))); }
  Future<void> _pagesSheet() async { await showModalBottomSheet<void>(context: context, showDragHandle: true, builder: (_) => SafeArea(child: Column(mainAxisSize: MainAxisSize.min, children: [const _Header('Pages', 'Multi-page project workspace'), ...List.generate(controller.project.pages.length, (i) => ListTile(leading: CircleAvatar(backgroundColor: i == controller.currentPageIndex ? _primary : Colors.black12, child: Text('${i + 1}', style: TextStyle(color: i == controller.currentPageIndex ? Colors.white : Colors.black87, fontWeight: FontWeight.w800))), title: Text(controller.project.pages[i].title), trailing: i == controller.currentPageIndex ? const Icon(Icons.check_circle_rounded, color: _primary) : null, onTap: () { controller.switchPage(i); Navigator.pop(context); })), const Divider(), ListTile(leading: const Icon(Icons.add_circle_outline_rounded), title: const Text('Add page'), onTap: () { controller.addPage(); Navigator.pop(context); }), ListTile(leading: const Icon(Icons.copy_all_outlined), title: const Text('Duplicate current page'), onTap: () { controller.duplicatePage(); Navigator.pop(context); }), ListTile(leading: const Icon(Icons.delete_outline_rounded), title: const Text('Delete current page'), enabled: controller.project.pages.length > 1, onTap: () { controller.deletePage(); Navigator.pop(context); })]))); }
  Future<void> _designSheet() async { await showModalBottomSheet<void>(context: context, showDragHandle: true, builder: (_) => SafeArea(child: Wrap(children: [const _Header('Canvas & Design', 'Set up your artboard before creating'), ListTile(leading: const Icon(Icons.palette_outlined), title: const Text('Background'), onTap: () { Navigator.pop(context); _backgroundSheet(); }), ListTile(leading: const Icon(Icons.aspect_ratio_rounded), title: const Text('Canvas size'), onTap: () { Navigator.pop(context); _canvasSizeDialog(); }), ListTile(leading: const Icon(Icons.layers_outlined), title: const Text('Pages'), onTap: () { Navigator.pop(context); _pagesSheet(); })]))); }
  Future<void> _backgroundSheet() async { final colors = [Colors.white, const Color(0xFF0F172A), const Color(0xFFF8FAFC), const Color(0xFFF5F3FF), const Color(0xFFFEF3C7), const Color(0xFFE0F2FE), const Color(0xFFFCE7F3)]; final c = await showModalBottomSheet<Color>(context: context, showDragHandle: true, builder: (_) => Padding(padding: const EdgeInsets.all(20), child: Wrap(spacing: 14, runSpacing: 14, children: colors.map((x) => InkWell(onTap: () => Navigator.pop(context, x), child: CircleAvatar(radius: 26, backgroundColor: x))).toList())); if (c != null) controller.setBackground(c); }
  Future<void> _canvasSizeDialog() async { final w = TextEditingController(text: controller.page.size.width.round().toString()); final h = TextEditingController(text: controller.page.size.height.round().toString()); final ok = await showDialog<bool>(context: context, builder: (d) => AlertDialog(title: const Text('Canvas Size', style: TextStyle(fontWeight: FontWeight.w900)), content: Row(children: [Expanded(child: TextField(controller: w, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Width'))), const SizedBox(width: 12), Expanded(child: TextField(controller: h, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Height')))]), actions: [TextButton(onPressed: () => Navigator.pop(d, false), child: const Text('Cancel')), FilledButton(onPressed: () => Navigator.pop(d, true), child: const Text('Resize'))])); if (ok == true) { final width = double.tryParse(w.text) ?? 1080; final height = double.tryParse(h.text) ?? 1080; controller.resizeCanvas(width, height); } w.dispose(); h.dispose(); }
  Future<void> _pickImage() async { final x = await _picker.pickImage(source: ImageSource.gallery); if (x == null) return; controller.addImage(await x.readAsBytes()); }
  Future<void> _save() async { try { await _repo.save(controller.project); if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Project saved locally'))); } catch (e) { if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Save failed: $e'))); } }
  Future<void> _exportMenu(String value) async { try { if (value == 'pdf') { await _export.sharePdf(controller.project); } else if (value == 'png') { await _export.exportPng(controller.page, _canvasKey); } else { await _export.exportJpg(controller.page, _canvasKey); } if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(value == 'pdf' ? 'PDF ready to share' : 'Export saved to gallery'))); } catch (e) { if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Export failed: $e'))); } }
}

class _Header extends StatelessWidget {
  final String title, subtitle;
  const _Header(this.title, this.subtitle);
  @override
  Widget build(BuildContext context) => Padding(padding: const EdgeInsets.fromLTRB(20, 8, 20, 8), child: Row(children: [Container(width: 42, height: 42, decoration: BoxDecoration(color: const Color(0xFF6D28D9).withValues(alpha: .10), borderRadius: BorderRadius.circular(13)), child: const Icon(Icons.auto_awesome_rounded, color: Color(0xFF6D28D9))), const SizedBox(width: 12), Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(title, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w900)), const SizedBox(height: 2), Text(subtitle, style: const TextStyle(fontSize: 11, color: Colors.black54, fontWeight: FontWeight.w600))]))]));
}

class _EffectsPanel extends StatefulWidget {
  final WorkspaceController controller;
  final DesignElement element;
  const _EffectsPanel({required this.controller, required this.element});
  @override
  State<_EffectsPanel> createState() => _EffectsPanelState();
}

class _EffectsPanelState extends State<_EffectsPanel> {
  late double stroke, blur, dx, dy;
  late Color strokeColor, shadowColor;
  @override
  void initState() { super.initState(); final e = widget.element; stroke = e.strokeWidth; blur = e.shadowBlur; dx = e.shadowOffsetX; dy = e.shadowOffsetY; strokeColor = Color(e.strokeColorValue); shadowColor = Color(e.shadowColorValue); }
  @override
  Widget build(BuildContext context) => SafeArea(child: Padding(padding: const EdgeInsets.fromLTRB(20, 4, 20, 24), child: Column(mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.start, children: [const _Header('Effects Studio', 'Stroke + soft shadow controls'), _slider('Stroke', stroke, 0, 40, (v) => setState(() => stroke = v)), _colorRow('Stroke color', strokeColor, (c) => setState(() => strokeColor = c)), const Divider(height: 20), _slider('Shadow blur', blur, 0, 80, (v) => setState(() => blur = v)), _slider('Shadow X', dx, -100, 100, (v) => setState(() => dx = v)), _slider('Shadow Y', dy, -100, 100, (v) => setState(() => dy = v)), _colorRow('Shadow color', shadowColor, (c) => setState(() => shadowColor = c)), const SizedBox(height: 10), SizedBox(width: double.infinity, child: FilledButton.icon(onPressed: () { widget.controller.setSelectedStroke(width: stroke, colorValue: strokeColor.toARGB32()); widget.controller.setSelectedShadow(blur: blur, offsetX: dx, offsetY: dy, colorValue: shadowColor.toARGB32()); Navigator.pop(context); }, icon: const Icon(Icons.check_rounded), label: const Text('Apply effects'))])));
  Widget _slider(String label, double value, double min, double max, ValueChanged<double> onChanged) => Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text('$label  ${value.toStringAsFixed(1)}', style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w800)), Slider(min: min, max: max, value: value, onChanged: onChanged)]);
  Widget _colorRow(String label, Color color, ValueChanged<Color> onChanged) => Row(children: [Expanded(child: Text(label, style: const TextStyle(fontWeight: FontWeight.w700))), InkWell(onTap: () async { final c = await showDialog<Color>(context: context, builder: (d) => AlertDialog(title: Text(label), content: Wrap(spacing: 10, runSpacing: 10, children: [Colors.black, Colors.white, const Color(0xFF6D28D9), const Color(0xFF0F766E), const Color(0xFFDC2626), const Color(0xFFF59E0B), const Color(0xFF2563EB)].map((x) => InkWell(onTap: () => Navigator.pop(d, x), child: CircleAvatar(backgroundColor: x, radius: 21))).toList()))); if (c != null) onChanged(c); }, child: CircleAvatar(backgroundColor: color, radius: 17, child: const Icon(Icons.colorize_rounded, size: 16, color: Colors.white))) ]);
}
