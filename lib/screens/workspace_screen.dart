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
  final CanvasSize size;

  const WorkspaceScreen({super.key, required this.size});

  @override
  State<WorkspaceScreen> createState() => _WorkspaceScreenState();
}

class _WorkspaceScreenState extends State<WorkspaceScreen> {
  late final WorkspaceController controller;
  final GlobalKey _canvasKey = GlobalKey();
  final ExportService _exportService = ExportService();
  final ProjectRepository _repository = ProjectRepository();
  final ImagePicker _imagePicker = ImagePicker();

  @override
  void initState() {
    super.initState();
    controller = WorkspaceController(newSize: widget.size);
  }

  @override
  void dispose() {
    controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: controller,
      builder: (context, _) {
        return Scaffold(
          backgroundColor: const Color(0xFFF1F3F8),
          appBar: _appBar(),
          body: Column(
            children: [Expanded(child: _editorArea()), _bottomToolbar()],
          ),
        );
      },
    );
  }

  PreferredSizeWidget _appBar() {
    return AppBar(
      elevation: 0,
      backgroundColor: Colors.white,
      surfaceTintColor: Colors.white,
      titleSpacing: 8,
      leading: IconButton(
        icon: const Icon(Icons.arrow_back_rounded),
        onPressed: () => Navigator.pop(context),
      ),
      title: const Text(
        'NaqshKaar Designer',
        style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800),
      ),
      actions: [
        IconButton(
          tooltip: 'Save project',
          onPressed: _saveProject,
          icon: const Icon(Icons.save_outlined),
        ),
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
        PopupMenuButton<String>(
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
        final availableWidth = constraints.maxWidth - 32;
        final availableHeight = constraints.maxHeight - 32;
        final scaleX = availableWidth / page.size.width;
        final scaleY = availableHeight / page.size.height;
        final scale = scaleX < scaleY ? scaleX : scaleY;

        return Center(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: InteractiveViewer(
              minScale: .25,
              maxScale: 4,
              boundaryMargin: const EdgeInsets.all(100),
              child: Transform.scale(
                scale: scale,
                alignment: Alignment.topLeft,
                child: SizedBox(
                  width: page.size.width,
                  height: page.size.height,
                  child: DesignCanvas(
                    controller: controller,
                    repaintKey: _canvasKey,
                  ),
                ),
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _bottomToolbar() {
    final selected = controller.selected;
    return SafeArea(
      top: false,
      child: Container(
        constraints: const BoxConstraints(minHeight: 88, maxHeight: 190),
        padding: const EdgeInsets.fromLTRB(10, 8, 10, 10),
        decoration: const BoxDecoration(
          color: Colors.white,
          boxShadow: [
            BoxShadow(
              blurRadius: 14,
              offset: Offset(0, -4),
              color: Color(0x14000000),
            ),
          ],
        ),
        child: selected == null ? _mainTools() : _selectedTools(selected),
      ),
    );
  }

  Widget _mainTools() {
    return Row(
      children: [
        _tool(Icons.text_fields_rounded, 'Text', _addText),
        _tool(Icons.crop_square_rounded, 'Shape', () => controller.addShape()),
        _tool(Icons.image_outlined, 'Image', _pickImage),
        _tool(Icons.layers_outlined, 'Pages', _showPages),
        _tool(Icons.more_horiz_rounded, 'More', _showMore),
      ],
    );
  }

  Widget _selectedTools(DesignElement selected) {
    final isText = selected.kind == ElementKind.text;
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        SizedBox(
          height: 48,
          child: ListView(
            scrollDirection: Axis.horizontal,
            children: [
              _compactTool(Icons.edit_outlined, 'Edit', isText ? _editText : null),
              if (isText)
                _compactTool(
                  Icons.format_size_rounded,
                  '${selected.fontSize.round()}',
                  () => _fontSizeDialog(selected),
                ),
              if (isText)
                _compactToggle(Icons.format_bold_rounded, selected.bold, controller.toggleSelectedBold),
              if (isText)
                _compactToggle(Icons.format_italic_rounded, selected.italic, controller.toggleSelectedItalic),
              if (isText)
                _compactTool(Icons.format_align_center_rounded, 'Align', _alignmentDialog),
              _compactTool(Icons.palette_outlined, 'Color', _colorDialog),
              _compactTool(
                selected.locked ? Icons.lock_rounded : Icons.lock_open_rounded,
                selected.locked ? 'Locked' : 'Lock',
                controller.toggleSelectedLock,
              ),
              _compactTool(Icons.copy_outlined, 'Copy', controller.duplicateSelected),
              _compactTool(Icons.delete_outline_rounded, 'Delete', controller.deleteSelected),
            ],
          ),
        ),
        SizedBox(
          height: 44,
          child: Row(
            children: [
              Expanded(
                child: Text(
                  selected.kind == ElementKind.text
                      ? 'Text element selected'
                      : '${selected.kind.name[0].toUpperCase()}${selected.kind.name.substring(1)} selected',
                  style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              IconButton(
                tooltip: 'Send backward',
                onPressed: controller.sendSelectedToBack,
                icon: const Icon(Icons.vertical_align_bottom_rounded),
              ),
              IconButton(
                tooltip: 'Bring forward',
                onPressed: controller.bringSelectedToFront,
                icon: const Icon(Icons.vertical_align_top_rounded),
              ),
              IconButton(
                tooltip: 'Pages',
                onPressed: _showPages,
                icon: const Icon(Icons.layers_outlined),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _tool(IconData icon, String label, VoidCallback onTap) {
    return Expanded(
      child: InkWell(
        borderRadius: BorderRadius.circular(14),
        onTap: onTap,
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 25, color: const Color(0xFF5B21B6)),
            const SizedBox(height: 5),
            Text(label, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700)),
          ],
        ),
      ),
    );
  }

  Widget _compactTool(IconData icon, String label, VoidCallback? onTap) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 4),
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: onTap,
        child: Container(
          width: 66,
          padding: const EdgeInsets.symmetric(horizontal: 5),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, size: 20, color: onTap == null ? Colors.black26 : const Color(0xFF5B21B6)),
              const SizedBox(height: 2),
              Text(label, style: TextStyle(fontSize: 9, fontWeight: FontWeight.w700, color: onTap == null ? Colors.black26 : Colors.black87)),
            ],
          ),
        ),
      ),
    );
  }

  Widget _compactToggle(IconData icon, bool active, VoidCallback onTap) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 4),
      child: IconButton(
        tooltip: active ? 'On' : 'Off',
        onPressed: onTap,
        style: IconButton.styleFrom(
          backgroundColor: active ? const Color(0xFFEDE9FE) : Colors.transparent,
        ),
        icon: Icon(icon, color: active ? const Color(0xFF5B21B6) : Colors.black54),
      ),
    );
  }

  Future<void> _addText() async {
    final text = await _textDialog(initial: 'اپنا متن یہاں لکھیں');
    if (text == null || text.trim().isEmpty) return;
    controller.addText(text: text.trim());
  }

  Future<void> _editText() async {
    final selected = controller.selected;
    if (selected == null) return;
    final text = await _textDialog(initial: selected.text);
    if (text == null) return;
    controller.editSelectedText(text);
  }

  Future<String?> _textDialog({required String initial}) async {
    final textController = TextEditingController(text: initial);
    return showDialog<String>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Urdu Text'),
        content: TextField(
          controller: textController,
          autofocus: true,
          maxLines: 6,
          textDirection: TextDirection.rtl,
          decoration: const InputDecoration(
            hintText: 'اپنا متن یہاں لکھیں',
            border: OutlineInputBorder(),
          ),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(dialogContext), child: const Text('Cancel')),
          FilledButton(onPressed: () => Navigator.pop(dialogContext, textController.text), child: const Text('Apply')),
        ],
      ),
    );
  }

  Future<void> _fontSizeDialog(DesignElement selected) async {
    double value = selected.fontSize;
    final result = await showDialog<double>(
      context: context,
      builder: (dialogContext) => StatefulBuilder(
        builder: (context, setState) => AlertDialog(
          title: const Text('Font size'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('${value.round()} px', style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w800)),
              Slider(
                min: 8,
                max: 200,
                value: value.clamp(8, 200),
                onChanged: (v) => setState(() => value = v),
              ),
            ],
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(dialogContext), child: const Text('Cancel')),
            FilledButton(onPressed: () => Navigator.pop(dialogContext, value), child: const Text('Apply')),
          ],
        ),
      ),
    );
    if (result != null) controller.setSelectedFontSize(result);
  }

  Future<void> _alignmentDialog() async {
    final selected = controller.selected;
    if (selected == null) return;
    final result = await showModalBottomSheet<TextAlign>(
      context: context,
      showDragHandle: true,
      builder: (context) => SafeArea(
        child: Wrap(
          children: [
            ListTile(leading: const Icon(Icons.format_align_left), title: const Text('Left'), onTap: () => Navigator.pop(context, TextAlign.left)),
            ListTile(leading: const Icon(Icons.format_align_center), title: const Text('Center'), onTap: () => Navigator.pop(context, TextAlign.center)),
            ListTile(leading: const Icon(Icons.format_align_right), title: const Text('Right'), onTap: () => Navigator.pop(context, TextAlign.right)),
            ListTile(leading: const Icon(Icons.format_align_justify), title: const Text('Justify'), onTap: () => Navigator.pop(context, TextAlign.justify)),
          ],
        ),
      ),
    );
    if (result != null) controller.setSelectedAlign(result);
  }

  Future<void> _colorDialog() async {
    const colors = [
      Colors.black,
      Colors.white,
      Color(0xFFD4AF37),
      Color(0xFF7C3AED),
      Color(0xFF2563EB),
      Color(0xFFDC2626),
      Color(0xFF059669),
      Color(0xFFF59E0B),
      Color(0xFFEC4899),
    ];
    await showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      builder: (context) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Wrap(
            spacing: 14,
            runSpacing: 14,
            children: [
              for (final color in colors)
                GestureDetector(
                  onTap: () {
                    controller.updateSelected(colorValue: color.toARGB32());
                    Navigator.pop(context);
                  },
                  child: Container(
                    width: 54,
                    height: 54,
                    decoration: BoxDecoration(
                      color: color,
                      shape: BoxShape.circle,
                      border: Border.all(color: Colors.black12, width: 2),
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _pickImage() async {
    try {
      final result = await _imagePicker.pickImage(source: ImageSource.gallery);
      if (result == null) return;
      controller.addImage(await result.readAsBytes());
    } catch (_) {
      _message('Image import failed.');
    }
  }

  Future<void> _handleMenu(String value) async {
    try {
      switch (value) {
        case 'png':
          final bytes = await _exportService.capturePng(
            _canvasKey,
            controller.page.size.width,
            controller.page.size.height,
          );
          await _exportService.savePng(bytes, 'naqshkaar_design');
          _message('PNG saved successfully.');
          break;
        case 'jpg':
          final png = await _exportService.capturePng(
            _canvasKey,
            controller.page.size.width,
            controller.page.size.height,
          );
          await _exportService.saveJpeg(await _exportService.pngToJpeg(png), 'naqshkaar_design');
          _message('JPG saved successfully.');
          break;
        case 'pdf':
          final png = await _exportService.capturePng(
            _canvasKey,
            controller.page.size.width,
            controller.page.size.height,
          );
          await _exportService.sharePdf(
            png,
            controller.page.size.width,
            controller.page.size.height,
            'naqshkaar_design.pdf',
          );
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

  void _showPages() {
    showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      builder: (context) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(16, 4, 16, 24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text('Pages', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w800)),
              const SizedBox(height: 12),
              ...List.generate(controller.project.pages.length, (index) {
                final page = controller.project.pages[index];
                return ListTile(
                  selected: controller.currentPageIndex == index,
                  leading: CircleAvatar(child: Text('${index + 1}')),
                  title: Text(page.title),
                  subtitle: Text('${page.size.width.toInt()} × ${page.size.height.toInt()}'),
                  onTap: () {
                    controller.switchPage(index);
                    Navigator.pop(context);
                  },
                );
              }),
              const Divider(),
              Row(
                children: [
                  Expanded(child: OutlinedButton.icon(onPressed: () { controller.addPage(); Navigator.pop(context); }, icon: const Icon(Icons.add_rounded), label: const Text('Add Page'))),
                  const SizedBox(width: 10),
                  Expanded(child: OutlinedButton.icon(onPressed: () { controller.duplicatePage(); Navigator.pop(context); }, icon: const Icon(Icons.copy_outlined), label: const Text('Duplicate'))),
                ],
              ),
              if (controller.project.pages.length > 1)
                Padding(
                  padding: const EdgeInsets.only(top: 10),
                  child: OutlinedButton.icon(
                    onPressed: () { controller.deletePage(); Navigator.pop(context); },
                    icon: const Icon(Icons.delete_outline),
                    label: const Text('Delete current page'),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }

  void _showMore() {
    showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      builder: (context) => SafeArea(
        child: Wrap(
          children: [
            const ListTile(title: Text('Design Tools', style: TextStyle(fontWeight: FontWeight.w800, fontSize: 18))),
            ListTile(leading: const Icon(Icons.delete_outline_rounded), title: const Text('Delete selected'), onTap: () { controller.deleteSelected(); Navigator.pop(context); }),
            ListTile(leading: const Icon(Icons.copy_all_outlined), title: const Text('Duplicate selected'), onTap: () { controller.duplicateSelected(); Navigator.pop(context); }),
            ListTile(leading: const Icon(Icons.vertical_align_top_rounded), title: const Text('Bring to front'), onTap: () { controller.bringSelectedToFront(); Navigator.pop(context); }),
            ListTile(leading: const Icon(Icons.vertical_align_bottom_rounded), title: const Text('Send to back'), onTap: () { controller.sendSelectedToBack(); Navigator.pop(context); }),
            ListTile(leading: const Icon(Icons.visibility_off_outlined), title: const Text('Hide selected'), onTap: () { controller.toggleSelectedHidden(); Navigator.pop(context); }),
            ListTile(leading: const Icon(Icons.format_color_fill_outlined), title: const Text('Background'), onTap: () { Navigator.pop(context); _showBackgroundPicker(); }),
            ListTile(leading: const Icon(Icons.folder_open_outlined), title: const Text('Pick image file'), onTap: () async { Navigator.pop(context); await _pickImageFile(); }),
          ],
        ),
      ),
    );
  }

  Future<void> _pickImageFile() async {
    try {
      final result = await FilePicker.platform.pickFiles(type: FileType.image, withData: true);
      if (result == null || result.files.isEmpty) return;
      final PlatformFile file = result.files.first;
      final Uint8List? bytes = file.bytes;
      if (bytes == null) {
        _message('Could not read image.');
        return;
      }
      controller.addImage(bytes);
    } catch (_) {
      _message('Could not import image.');
    }
  }

  void _showBackgroundPicker() {
    const colors = [Colors.white, Color(0xFFF7F8FC), Color(0xFF111827), Color(0xFF0F172A), Color(0xFFEDE9FE), Color(0xFFFEF3C7), Color(0xFFDCFCE7), Color(0xFFFCE7F3)];
    showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      builder: (context) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Wrap(
            spacing: 14,
            runSpacing: 14,
            children: [
              for (final color in colors)
                GestureDetector(
                  onTap: () { controller.setBackground(color); Navigator.pop(context); },
                  child: Container(width: 58, height: 58, decoration: BoxDecoration(color: color, shape: BoxShape.circle, border: Border.all(color: Colors.black12, width: 2))),
                ),
            ],
          ),
        ),
      ),
    );
  }

  void _message(String text) {
    if (!mounted) return;
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(SnackBar(content: Text(text), behavior: SnackBarBehavior.floating));
  }
}
