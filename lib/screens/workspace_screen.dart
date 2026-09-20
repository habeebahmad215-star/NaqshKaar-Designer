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

  static const Color _primary = Color(0xFF6D28D9);
  static const Color _background = Color(0xFFF5F3F9);

  @override
  void initState() {
    super.initState();
    controller = WorkspaceController(
      initial: widget.initialProject,
      newSize: widget.size,
    );
  }

  @override
  void dispose() {
    _transform.dispose();
    controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: controller,
      builder: (context, child) {
        return Scaffold(
          backgroundColor: _background,
          appBar: _buildAppBar(),
          body: Column(
            children: [
              Expanded(child: _buildCanvasArea()),
              _buildToolbar(),
            ],
          ),
        );
      },
    );
  }

  PreferredSizeWidget _buildAppBar() {
    return AppBar(
      backgroundColor: Colors.white,
      surfaceTintColor: Colors.white,
      elevation: 0,
      leading: IconButton(
        tooltip: 'Back',
        icon: const Icon(Icons.arrow_back_rounded),
        onPressed: () => Navigator.pop(context),
      ),
      titleSpacing: 0,
      title: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            controller.project.name,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w900),
          ),
          Text(
            'Page ${controller.currentPageIndex + 1}  •  '
            '${controller.page.size.width.round()} × ${controller.page.size.height.round()}',
            style: const TextStyle(fontSize: 10, color: Colors.black54),
          ),
        ],
      ),
      actions: [
        IconButton(
          tooltip: 'Undo',
          onPressed: controller.canUndo ? controller.undo : null,
          icon: const Icon(Icons.undo_rounded),
        ),
        IconButton(
          tooltip: 'Redo',
          onPressed: controller.canRedo ? controller.redo : null,
          icon: const Icon(Icons.redo_rounded),
        ),
        IconButton(
          tooltip: 'Save',
          onPressed: _save,
          icon: const Icon(Icons.save_outlined),
        ),
        PopupMenuButton<String>(
          onSelected: _exportMenu,
          itemBuilder: (context) => const [
            PopupMenuItem(value: 'png', child: Text('Export PNG')),
            PopupMenuItem(value: 'jpg', child: Text('Export JPG')),
            PopupMenuItem(value: 'pdf', child: Text('Share PDF')),
          ],
        ),
      ],
    );
  }

  Widget _buildCanvasArea() {
    return LayoutBuilder(
      builder: (context, constraints) {
        final availableWidth = (constraints.maxWidth - 28)
            .clamp(120.0, double.infinity)
            .toDouble();
        final availableHeight = (constraints.maxHeight - 28)
            .clamp(120.0, double.infinity)
            .toDouble();
        final widthScale = availableWidth / controller.page.size.width;
        final heightScale = availableHeight / controller.page.size.height;
        final fitScale = (widthScale < heightScale ? widthScale : heightScale)
            .clamp(0.05, 1.0)
            .toDouble();

        return AnimatedBuilder(
          animation: _transform,
          builder: (context, child) {
            final zoom = _transform.value.getMaxScaleOnAxis().clamp(0.5, 4.0).toDouble();
            return Padding(
              padding: const EdgeInsets.all(14),
              child: Stack(
                children: [
                  Positioned.fill(
                    child: InteractiveViewer(
                      transformationController: _transform,
                      minScale: 0.5,
                      maxScale: 4,
                      constrained: false,
                      boundaryMargin: const EdgeInsets.all(240),
                      child: Center(
                        child: SizedBox(
                          width: availableWidth,
                          height: availableHeight,
                          child: FittedBox(
                            fit: BoxFit.contain,
                            child: DesignCanvas(
                              controller: controller,
                              repaintKey: _canvasKey,
                              interactionScale: fitScale * zoom,
                            ),
                          ),
                        ),
                      ),
                    ),
                  ),
                  Positioned(
                    top: 8,
                    right: 8,
                    child: _viewButton(
                      Icons.center_focus_strong_rounded,
                      'Reset view',
                      () => _transform.value = Matrix4.identity(),
                    ),
                  ),
                  Positioned(
                    left: 8,
                    bottom: 8,
                    child: Material(
                      color: Colors.white,
                      elevation: 2,
                      borderRadius: BorderRadius.circular(18),
                      child: Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 11, vertical: 7),
                        child: Text(
                          '${(zoom * 100).round()}%',
                          style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            );
          },
        );
      },
    );
  }

  Widget _viewButton(IconData icon, String tooltip, VoidCallback onTap) {
    return Material(
      color: Colors.white,
      elevation: 3,
      borderRadius: BorderRadius.circular(14),
      child: IconButton(
        tooltip: tooltip,
        onPressed: onTap,
        icon: Icon(icon, size: 21),
      ),
    );
  }

  Widget _buildToolbar() {
    return SafeArea(
      top: false,
      child: Container(
        padding: const EdgeInsets.fromLTRB(8, 7, 8, 8),
        decoration: const BoxDecoration(
          color: Colors.white,
          boxShadow: [
            BoxShadow(blurRadius: 20, offset: Offset(0, -5), color: Color(0x18000000)),
          ],
        ),
        child: controller.selected == null
            ? _mainToolbar()
            : _selectedToolbar(controller.selected!),
      ),
    );
  }

  Widget _mainToolbar() {
    return Row(
      children: [
        _mainTool(Icons.text_fields_rounded, 'Text', _addText),
        _mainTool(Icons.crop_square_rounded, 'Shape', controller.addShape),
        _mainTool(Icons.image_outlined, 'Image', _pickImage),
        _mainTool(Icons.layers_outlined, 'Pages', _pagesSheet),
        _mainTool(Icons.tune_rounded, 'Design', _designSheet),
      ],
    );
  }

  Widget _mainTool(IconData icon, String label, VoidCallback onTap) {
    return Expanded(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(14),
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 5),
          child: Column(
            children: [
              Icon(icon, color: _primary, size: 25),
              const SizedBox(height: 4),
              Text(label, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800)),
            ],
          ),
        ),
      ),
    );
  }

  Widget _selectedToolbar(DesignElement element) {
    final isText = element.kind == ElementKind.text;
    final isShape = element.kind == ElementKind.shape;
    final tools = <Widget>[
      if (isText) _tool(Icons.edit_rounded, 'Edit', _editText),
      if (isText) _tool(Icons.font_download_outlined, 'Font', _fontSheet),
      if (isText) _tool(Icons.format_size_rounded, '${element.fontSize.round()}', () => _fontSize(element)),
      if (isText) _toggleTool(Icons.format_bold_rounded, 'Bold', element.bold, controller.toggleSelectedBold),
      if (isText) _toggleTool(Icons.format_italic_rounded, 'Italic', element.italic, controller.toggleSelectedItalic),
      _tool(Icons.palette_outlined, 'Color', _colorSheet),
      _tool(Icons.auto_awesome_rounded, 'Effects', _effectsSheet),
      if (isText) _tool(Icons.format_line_spacing_rounded, 'Spacing', _spacingSheet),
      if (isShape) _tool(Icons.rounded_corner, 'Corners', _radius),
      _tool(Icons.opacity_rounded, 'Opacity', _opacity),
      if (isText) _tool(Icons.format_align_center_rounded, 'Align', _alignSheet),
      if (isText) _tool(Icons.translate_rounded, 'RTL/LTR', _directionSheet),
      _tool(Icons.open_with_rounded, 'Arrange', _arrangeSheet),
      _tool(Icons.more_horiz_rounded, 'More', _moreSheet),
    ];

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        SizedBox(
          height: 60,
          child: ListView(scrollDirection: Axis.horizontal, children: tools),
        ),
        Row(
          children: [
            Expanded(
              child: Text(
                _elementLabel(element),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800),
              ),
            ),
            IconButton(
              tooltip: 'Duplicate',
              visualDensity: VisualDensity.compact,
              onPressed: controller.duplicateSelected,
              icon: const Icon(Icons.copy_outlined),
            ),
            IconButton(
              tooltip: element.locked ? 'Unlock' : 'Lock',
              visualDensity: VisualDensity.compact,
              onPressed: controller.toggleSelectedLock,
              icon: Icon(element.locked ? Icons.lock_rounded : Icons.lock_open_rounded),
            ),
            IconButton(
              tooltip: 'Delete',
              visualDensity: VisualDensity.compact,
              onPressed: controller.deleteSelected,
              icon: const Icon(Icons.delete_outline_rounded),
            ),
          ],
        ),
      ],
    );
  }

  String _elementLabel(DesignElement element) {
    switch (element.kind) {
      case ElementKind.text:
        return 'Urdu Text • ${element.fontFamily == 'JameelNoori' ? 'Gulzar' : element.fontFamily}';
      case ElementKind.image:
        return 'Image • ${element.width.round()} × ${element.height.round()}';
      case ElementKind.shape:
        return 'Shape • ${element.width.round()} × ${element.height.round()}';
    }
  }

  Widget _tool(IconData icon, String label, VoidCallback onTap) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 3),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: SizedBox(
          width: 64,
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, color: _primary, size: 21),
              const SizedBox(height: 3),
              Text(label, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 9, fontWeight: FontWeight.w800)),
            ],
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
          width: 64,
          decoration: BoxDecoration(
            color: active ? _primary.withValues(alpha: 0.10) : Colors.transparent,
            borderRadius: BorderRadius.circular(12),
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, color: active ? _primary : Colors.black54, size: 21),
              const SizedBox(height: 3),
              Text(label, style: TextStyle(fontSize: 9, fontWeight: FontWeight.w800, color: active ? _primary : Colors.black87)),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _addText() async {
    final value = await _textDialog('Add Urdu Text', 'اپنا متن یہاں لکھیں');
    if (value != null && value.trim().isNotEmpty) controller.addText(text: value.trim());
  }

  Future<void> _editText() async {
    final element = controller.selected;
    if (element == null) return;
    controller.startContinuousEdit();
    final value = await _textDialog('Edit Text', element.text, livePreview: true);
    if (value == null) {
      controller.cancelContinuousEdit();
    } else {
      controller.finishContinuousEdit();
    }
  }

  Future<String?> _textDialog(String title, String initial, {bool livePreview = false}) async {
    final textController = TextEditingController(text: initial);
    final result = await showDialog<String>(
      context: context,
      builder: (dialogContext) {
        return AlertDialog(
          title: Text(title, style: const TextStyle(fontWeight: FontWeight.w900)),
          content: TextField(
            controller: textController,
            autofocus: true,
            maxLines: 7,
            textDirection: TextDirection.rtl,
            style: const TextStyle(fontFamily: 'Gulzar', fontSize: 23),
            onChanged: livePreview ? controller.editSelectedText : null,
            decoration: const InputDecoration(hintText: 'اردو متن', border: OutlineInputBorder()),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(dialogContext), child: const Text('Cancel')),
            FilledButton(onPressed: () => Navigator.pop(dialogContext, textController.text), child: const Text('Apply')),
          ],
        );
      },
    );
    textController.dispose();
    return result;
  }

  Future<void> _fontSheet() async {
    final element = controller.selected;
    if (element == null) return;
    final family = await showModalBottomSheet<String>(
      context: context,
      showDragHandle: true,
      builder: (sheetContext) {
        return SafeArea(
          child: ListView(
            shrinkWrap: true,
            children: [
              const _SheetHeader('Urdu Typography', 'Premium Nastaliq font families'),
              _fontTile('Gulzar', 'Contemporary Nastaliq', 'Gulzar', element.fontFamily),
              _fontTile('Noto Nastaliq Urdu', 'Google Fonts Nastaliq', 'NotoNastaliqUrdu', element.fontFamily),
            ],
          ),
        );
      },
    );
    if (family != null) controller.setSelectedFont(family);
  }

  Widget _fontTile(String title, String subtitle, String family, String current) {
    final active = current == family || (current == 'JameelNoori' && family == 'Gulzar');
    return ListTile(
      leading: CircleAvatar(
        backgroundColor: active ? _primary : Colors.black12,
        child: Icon(Icons.font_download_rounded, color: active ? Colors.white : Colors.black54),
      ),
      title: Text(title, style: TextStyle(fontFamily: family, fontSize: 21, fontWeight: FontWeight.w700)),
      subtitle: Text(subtitle),
      trailing: active ? const Icon(Icons.check_circle_rounded, color: _primary) : null,
      onTap: () => Navigator.pop(context, family),
    );
  }

  Future<void> _fontSize(DesignElement element) => _singleSlider('Font Size', element.fontSize, 5, 100, (v) => '${v.round()} px', controller.setSelectedFontSize);

  Future<void> _opacity() {
    final element = controller.selected;
    if (element == null) return Future.value();
    return _singleSlider('Opacity', element.opacity, 0, 1, (v) => '${(v * 100).round()}%', controller.setSelectedOpacity, divisions: 20);
  }

  Future<void> _radius() {
    final element = controller.selected;
    if (element == null) return Future.value();
    return _singleSlider('Corner Radius', element.radius, 0, 240, (v) => '${v.round()} px', controller.setSelectedRadius);
  }

  Future<void> _singleSlider(
    String title,
    double initial,
    double min,
    double max,
    String Function(double) display,
    ValueChanged<double> apply, {
    int? divisions,
  }) async {
    double value = initial.clamp(min, max).toDouble();
    controller.startContinuousEdit();
    await showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      builder: (sheetContext) {
        return StatefulBuilder(
          builder: (context, setSheetState) {
            return SafeArea(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(20, 8, 20, 24),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(title, style: const TextStyle(fontSize: 19, fontWeight: FontWeight.w900)),
                    const SizedBox(height: 8),
                    Text(display(value), style: const TextStyle(fontSize: 26, fontWeight: FontWeight.w900, color: _primary)),
                    Slider(min: min, max: max, divisions: divisions, value: value, onChanged: (newValue) { setSheetState(() => value = newValue); apply(newValue); }),
                    SizedBox(
                      width: double.infinity,
                      child: FilledButton.icon(
                        onPressed: () {
                          controller.finishContinuousEdit();
                          Navigator.pop(sheetContext);
                        },
                        icon: const Icon(Icons.check_rounded),
                        label: const Text('Apply'),
                      ),
                    ),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
    controller.finishContinuousEdit();
  }

  Future<void> _colorSheet() async {
    final element = controller.selected;
    if (element == null) return;
    const colors = [Colors.black, Colors.white, _primary, Color(0xFF0F766E), Color(0xFFDC2626), Color(0xFFF59E0B), Color(0xFF2563EB), Color(0xFF7C2D12), Color(0xFFDB2777)];
    final color = await showModalBottomSheet<Color>(
      context: context,
      showDragHandle: true,
      builder: (sheetContext) {
        return SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Wrap(
              spacing: 14,
              runSpacing: 14,
              children: colors.map((color) {
                return InkWell(
                  onTap: () => Navigator.pop(sheetContext, color),
                  borderRadius: BorderRadius.circular(30),
                  child: CircleAvatar(
                    radius: 25,
                    backgroundColor: color,
                    child: color.toARGB32() == element.colorValue ? const Icon(Icons.check_rounded, color: Colors.white) : null,
                  ),
                );
              }).toList(),
            ),
          ),
        );
      },
    );
    if (color != null) controller.updateSelected(colorValue: color.toARGB32());
  }

  Future<void> _effectsSheet() async {
    final element = controller.selected;
    if (element == null) return;
    double strokeWidth = element.strokeWidth;
    double shadowBlur = element.shadowBlur;
    double shadowX = element.shadowOffsetX;
    double shadowY = element.shadowOffsetY;

    await showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      showDragHandle: true,
      builder: (sheetContext) {
        return StatefulBuilder(
          builder: (context, setSheetState) {
            return SafeArea(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(20, 8, 20, 24),
                child: SingleChildScrollView(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const _SheetHeader('Effects Studio', 'Stroke and soft shadow controls'),
                      _effectSlider('Stroke', strokeWidth, 0, 40, (v) => setSheetState(() => strokeWidth = v)),
                      _effectSlider('Shadow Blur', shadowBlur, 0, 80, (v) => setSheetState(() => shadowBlur = v)),
                      _effectSlider('Shadow X', shadowX, -100, 100, (v) => setSheetState(() => shadowX = v)),
                      _effectSlider('Shadow Y', shadowY, -100, 100, (v) => setSheetState(() => shadowY = v)),
                      const SizedBox(height: 8),
                      SizedBox(
                        width: double.infinity,
                        child: FilledButton.icon(
                          onPressed: () {
                            controller.setSelectedStroke(width: strokeWidth, colorValue: element.strokeColorValue == 0 ? Colors.black.toARGB32() : element.strokeColorValue);
                            controller.setSelectedShadow(blur: shadowBlur, offsetX: shadowX, offsetY: shadowY, colorValue: element.shadowColorValue == 0 ? Colors.black54.toARGB32() : element.shadowColorValue);
                            Navigator.pop(sheetContext);
                          },
                          icon: const Icon(Icons.check_rounded),
                          label: const Text('Apply effects'),
                        ),
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
  }

  Widget _effectSlider(String label, double value, double min, double max, ValueChanged<double> onChanged) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('$label  ${value.toStringAsFixed(1)}', style: const TextStyle(fontWeight: FontWeight.w700)),
        Slider(min: min, max: max, value: value, onChanged: onChanged, onChangeEnd: (_) => controller.finishContinuousEdit()),
      ],
    );
  }

  Future<void> _spacingSheet() async {
    final element = controller.selected;
    if (element == null) return;
    double letterSpacing = element.letterSpacing;
    double lineHeight = element.lineHeight;

    await showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      builder: (sheetContext) {
        return StatefulBuilder(
          builder: (context, setSheetState) {
            return SafeArea(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(20, 8, 20, 24),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const _SheetHeader('Typography Spacing', 'Fine control for Nastaliq composition'),
                    _effectSlider('Letter Spacing', letterSpacing, -10, 20, (v) => setSheetState(() => letterSpacing = v)),
                    _effectSlider('Line Height', lineHeight, 0.7, 3, (v) => setSheetState(() => lineHeight = v)),
                    SizedBox(
                      width: double.infinity,
                      child: FilledButton.icon(
                        onPressed: () {
                          controller.setSelectedTypography(letterSpacing: letterSpacing, lineHeight: lineHeight);
                          Navigator.pop(sheetContext);
                        },
                        icon: const Icon(Icons.check_rounded),
                        label: const Text('Apply typography'),
                      ),
                    ),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }

  Future<void> _alignSheet() async {
    final value = await _choiceSheet<TextAlign>('Text Alignment', [TextAlign.left, TextAlign.center, TextAlign.right, TextAlign.justify], (value) => value.name);
    if (value != null) controller.setSelectedAlign(value);
  }

  Future<void> _directionSheet() async {
    final value = await _choiceSheet<TextDirection>('Text Direction', [TextDirection.rtl, TextDirection.ltr], (value) => value == TextDirection.rtl ? 'Right to left (Urdu)' : 'Left to right');
    if (value != null) controller.setSelectedDirection(value);
  }

  Future<T?> _choiceSheet<T>(String title, List<T> values, String Function(T) label) {
    return showModalBottomSheet<T>(
      context: context,
      showDragHandle: true,
      builder: (sheetContext) {
        return SafeArea(
          child: ListView(
            shrinkWrap: true,
            children: [
              _SheetHeader(title, 'Choose a professional layout setting'),
              ...values.map((value) => ListTile(title: Text(label(value), style: const TextStyle(fontWeight: FontWeight.w700)), onTap: () => Navigator.pop(sheetContext, value))),
            ],
          ),
        );
      },
    );
  }

  Future<void> _arrangeSheet() async {
    await showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      builder: (sheetContext) {
        return SafeArea(
          child: Wrap(
            children: [
              const _SheetHeader('Arrange', 'Precise layer and position controls'),
              ListTile(leading: const Icon(Icons.vertical_align_top_rounded), title: const Text('Bring to front'), onTap: () { controller.bringSelectedToFront(); Navigator.pop(sheetContext); }),
              ListTile(leading: const Icon(Icons.vertical_align_bottom_rounded), title: const Text('Send to back'), onTap: () { controller.sendSelectedToBack(); Navigator.pop(sheetContext); }),
              ListTile(leading: const Icon(Icons.center_focus_strong_rounded), title: const Text('Center on canvas'), onTap: () { controller.centerSelected(); Navigator.pop(sheetContext); }),
            ],
          ),
        );
      },
    );
  }

  Future<void> _moreSheet() async {
    await showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      builder: (sheetContext) {
        return SafeArea(
          child: Wrap(
            children: [
              const _SheetHeader('Object', 'More professional editing actions'),
              ListTile(leading: const Icon(Icons.copy_rounded), title: const Text('Duplicate'), onTap: () { controller.duplicateSelected(); Navigator.pop(sheetContext); }),
              ListTile(leading: const Icon(Icons.visibility_off_outlined), title: const Text('Hide / Show'), onTap: () { controller.toggleSelectedHidden(); Navigator.pop(sheetContext); }),
              ListTile(leading: const Icon(Icons.rotate_left_rounded), title: const Text('Reset rotation'), onTap: () { controller.resetSelectedRotation(); Navigator.pop(sheetContext); }),
              ListTile(leading: const Icon(Icons.delete_outline_rounded), title: const Text('Delete'), onTap: () { controller.deleteSelected(); Navigator.pop(sheetContext); }),
            ],
          ),
        );
      },
    );
  }

  Future<void> _pagesSheet() async {
    await showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      builder: (sheetContext) {
        return SafeArea(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const _SheetHeader('Pages', 'Multi-page project workspace'),
              ...List.generate(controller.project.pages.length, (index) {
                final selected = index == controller.currentPageIndex;
                return ListTile(
                  leading: CircleAvatar(backgroundColor: selected ? _primary : Colors.black12, child: Text('${index + 1}', style: TextStyle(color: selected ? Colors.white : Colors.black87))),
                  title: Text(controller.project.pages[index].title),
                  trailing: selected ? const Icon(Icons.check_circle_rounded, color: _primary) : null,
                  onTap: () { controller.switchPage(index); Navigator.pop(sheetContext); },
                );
              }),
              const Divider(),
              ListTile(leading: const Icon(Icons.add_circle_outline_rounded), title: const Text('Add page'), onTap: () { controller.addPage(); Navigator.pop(sheetContext); }),
              ListTile(leading: const Icon(Icons.copy_all_outlined), title: const Text('Duplicate current page'), onTap: () { controller.duplicatePage(); Navigator.pop(sheetContext); }),
              ListTile(enabled: controller.project.pages.length > 1, leading: const Icon(Icons.delete_outline_rounded), title: const Text('Delete current page'), onTap: () { controller.deletePage(); Navigator.pop(sheetContext); }),
            ],
          ),
        );
      },
    );
  }

  Future<void> _designSheet() async {
    await showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      builder: (sheetContext) {
        return SafeArea(
          child: Wrap(
            children: [
              const _SheetHeader('Canvas & Design', 'Set up your artboard before creating'),
              ListTile(leading: const Icon(Icons.palette_outlined), title: const Text('Background'), onTap: () { Navigator.pop(sheetContext); _backgroundSheet(); }),
              ListTile(leading: const Icon(Icons.aspect_ratio_rounded), title: const Text('Canvas size'), onTap: () { Navigator.pop(sheetContext); _canvasSizeDialog(); }),
              ListTile(leading: const Icon(Icons.layers_outlined), title: const Text('Pages'), onTap: () { Navigator.pop(sheetContext); _pagesSheet(); }),
            ],
          ),
        );
      },
    );
  }

  Future<void> _backgroundSheet() async {
    const colors = [Colors.white, Color(0xFF0F172A), Color(0xFFF8FAFC), Color(0xFFF5F3FF), Color(0xFFFEF3C7), Color(0xFFE0F2FE), Color(0xFFFCE7F3)];
    final color = await showModalBottomSheet<Color>(
      context: context,
      showDragHandle: true,
      builder: (sheetContext) {
        return Padding(
          padding: const EdgeInsets.all(20),
          child: Wrap(
            spacing: 14,
            runSpacing: 14,
            children: colors.map((color) => InkWell(onTap: () => Navigator.pop(sheetContext, color), child: CircleAvatar(radius: 26, backgroundColor: color))).toList(),
          ),
        );
      },
    );
    if (color != null) controller.setBackground(color);
  }

  Future<void> _canvasSizeDialog() async {
    final widthController = TextEditingController(text: controller.page.size.width.round().toString());
    final heightController = TextEditingController(text: controller.page.size.height.round().toString());
    final accepted = await showDialog<bool>(
      context: context,
      builder: (dialogContext) {
        return AlertDialog(
          title: const Text('Canvas Size', style: TextStyle(fontWeight: FontWeight.w900)),
          content: Row(
            children: [
              Expanded(child: TextField(controller: widthController, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Width'))),
              const SizedBox(width: 12),
              Expanded(child: TextField(controller: heightController, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Height'))),
            ],
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(dialogContext, false), child: const Text('Cancel')),
            FilledButton(onPressed: () => Navigator.pop(dialogContext, true), child: const Text('Resize')),
          ],
        );
      },
    );
    if (accepted == true) {
      final width = (double.tryParse(widthController.text) ?? 1080).clamp(64, 16000).toDouble();
      final height = (double.tryParse(heightController.text) ?? 1080).clamp(64, 16000).toDouble();
      controller.resizeCanvas(width, height);
    }
    widthController.dispose();
    heightController.dispose();
  }

  Future<void> _pickImage() async {
    final picked = await _picker.pickImage(source: ImageSource.gallery);
    if (picked == null) return;
    controller.addImage(await picked.readAsBytes());
  }

  Future<void> _save() async {
    try {
      await _repo.save(controller.project);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Project saved locally')));
    } catch (error) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Save failed: $error')));
    }
  }

  Future<void> _exportMenu(String value) async {
    try {
      if (value == 'pdf') {
        await _export.sharePdf(controller.project);
      } else if (value == 'png') {
        await _export.exportPng(controller.page, _canvasKey);
      } else {
        await _export.exportJpg(controller.page, _canvasKey);
      }
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(value == 'pdf' ? 'PDF ready to share' : 'Export saved to gallery')));
    } catch (error) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Export failed: $error')));
    }
  }
}

class _SheetHeader extends StatelessWidget {
  final String title;
  final String subtitle;

  const _SheetHeader(this.title, this.subtitle);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 8, 20, 10),
      child: Row(
        children: [
          Container(
            width: 42,
            height: 42,
            decoration: BoxDecoration(
              color: const Color(0xFF6D28D9).withValues(alpha: 0.10),
              borderRadius: BorderRadius.circular(13),
            ),
            child: const Icon(Icons.auto_awesome_rounded, color: Color(0xFF6D28D9)),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w900)),
                const SizedBox(height: 2),
                Text(subtitle, style: const TextStyle(fontSize: 11, color: Colors.black54)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
