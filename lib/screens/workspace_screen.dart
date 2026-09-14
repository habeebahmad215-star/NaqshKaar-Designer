import 'dart:typed_data';

import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../models/design_models.dart';
import '../services/export_service.dart';
import '../state/workspace_controller.dart';
import '../widgets/design_canvas.dart';

class WorkspaceScreen extends StatefulWidget {
  final CanvasSize size;

  const WorkspaceScreen({
    super.key,
    required this.size,
  });

  @override
  State<WorkspaceScreen> createState() => _WorkspaceScreenState();
}

class _WorkspaceScreenState extends State<WorkspaceScreen> {
  late final WorkspaceController controller;
  final GlobalKey _canvasKey = GlobalKey();
  final ExportService _exportService = ExportService();
  final ImagePicker _imagePicker = ImagePicker();

  @override
  void initState() {
    super.initState();
    controller = WorkspaceController(
      newSize: widget.size,
    );
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
            children: [
              Expanded(
                child: _editorArea(),
              ),
              _bottomToolbar(),
            ],
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
      titleSpacing: 12,
      leading: IconButton(
        icon: const Icon(Icons.arrow_back_rounded),
        onPressed: () => Navigator.pop(context),
      ),
      title: const Text(
        'NaqshKaar Designer',
        style: TextStyle(
          fontSize: 18,
          fontWeight: FontWeight.w800,
        ),
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
        PopupMenuButton<String>(
          onSelected: _handleMenu,
          itemBuilder: (context) => const [
            PopupMenuItem(
              value: 'png',
              child: Text('Export PNG'),
            ),
            PopupMenuItem(
              value: 'jpg',
              child: Text('Export JPG'),
            ),
            PopupMenuItem(
              value: 'pdf',
              child: Text('Share PDF'),
            ),
          ],
        ),
      ],
    );
  }

  Widget _editorArea() {
    final page = controller.page;

    return LayoutBuilder(
      builder: (context, constraints) {
        final availableWidth =
            constraints.maxWidth - 32;
        final availableHeight =
            constraints.maxHeight - 32;

        final scaleX =
            availableWidth / page.size.width;
        final scaleY =
            availableHeight / page.size.height;

        final scale =
            scaleX < scaleY ? scaleX : scaleY;

        return Center(
          child: Container(
            padding: const EdgeInsets.all(16),
            child: InteractiveViewer(
              minScale: .25,
              maxScale: 4,
              boundaryMargin:
                  const EdgeInsets.all(100),
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
    return SafeArea(
      top: false,
      child: Container(
        height: 88,
        padding: const EdgeInsets.symmetric(
          horizontal: 12,
          vertical: 10,
        ),
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
        child: Row(
          children: [
            _tool(
              icon: Icons.text_fields_rounded,
              label: 'Text',
              onTap: () {
                controller.addText();
              },
            ),
            _tool(
              icon: Icons.crop_square_rounded,
              label: 'Shape',
              onTap: () {
                controller.addShape();
              },
            ),
            _tool(
              icon: Icons.image_outlined,
              label: 'Image',
              onTap: _pickImage,
            ),
            _tool(
              icon: Icons.layers_outlined,
              label: 'Pages',
              onTap: _showPages,
            ),
            _tool(
              icon: Icons.more_horiz_rounded,
              label: 'More',
              onTap: _showMore,
            ),
          ],
        ),
      ),
    );
  }

  Widget _tool({
    required IconData icon,
    required String label,
    required VoidCallback onTap,
  }) {
    return Expanded(
      child: InkWell(
        borderRadius: BorderRadius.circular(14),
        onTap: onTap,
        child: Column(
          mainAxisAlignment:
              MainAxisAlignment.center,
          children: [
            Icon(
              icon,
              size: 25,
              color: const Color(0xFF5B21B6),
            ),
            const SizedBox(height: 5),
            Text(
              label,
              style: const TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w700,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _pickImage() async {
    try {
      final result =
          await _imagePicker.pickImage(
        source: ImageSource.gallery,
      );

      if (result == null) return;

      final bytes = await result.readAsBytes();

      controller.addImage(bytes);
    } catch (e) {
      _message('Image import failed.');
    }
  }

  Future<void> _handleMenu(String value) async {
    try {
      switch (value) {
        case 'png':
          final bytes =
              await _exportService.capturePng(
            _canvasKey,
            controller.page.size.width,
            controller.page.size.width,
          );

          await _exportService.savePng(
            bytes,
            'naqshkaar_design',
          );

          _message('PNG saved successfully.');
          break;

        case 'jpg':
          final png =
              await _exportService.capturePng(
            _canvasKey,
            controller.page.size.width,
            controller.page.size.width,
          );

          final jpg =
              await _exportService.pngToJpeg(png);

          await _exportService.saveJpeg(
            jpg,
            'naqshkaar_design',
          );

          _message('JPG saved successfully.');
          break;

        case 'pdf':
          final png =
              await _exportService.capturePng(
            _canvasKey,
            controller.page.size.width,
            controller.page.size.width,
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

  void _showPages() {
    showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      builder: (context) {
        return SafeArea(
          child: Padding(
            padding: const EdgeInsets.fromLTRB(
              16,
              4,
              16,
              24,
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Text(
                  'Pages',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                const SizedBox(height: 12),
                ...List.generate(
                  controller.project.pages.length,
                  (index) {
                    final page =
                        controller.project.pages[index];

                    return ListTile(
                      selected:
                          controller.currentPageIndex ==
                              index,
                      leading: CircleAvatar(
                        child: Text(
                          '${index + 1}',
                        ),
                      ),
                      title: Text(page.title),
                      subtitle: Text(
                        '${page.size.width.toInt()} × '
                        '${page.size.height.toInt()}',
                      ),
                      onTap: () {
                        controller.switchPage(index);
                        Navigator.pop(context);
                      },
                    );
                  },
                ),
                const Divider(),
                Row(
                  children: [
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: () {
                          controller.addPage();
                          Navigator.pop(context);
                        },
                        icon: const Icon(
                          Icons.add_rounded,
                        ),
                        label: const Text('Add Page'),
                      ),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: () {
                          controller.duplicatePage();
                          Navigator.pop(context);
                        },
                        icon: const Icon(
                          Icons.copy_outlined,
                        ),
                        label: const Text('Duplicate'),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  void _showMore() {
    showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      builder: (context) {
        return SafeArea(
          child: Wrap(
            children: [
              const ListTile(
                title: Text(
                  'Design Tools',
                  style: TextStyle(
                    fontWeight: FontWeight.w800,
                    fontSize: 18,
                  ),
                ),
              ),
              ListTile(
                leading: const Icon(
                  Icons.delete_outline_rounded,
                ),
                title: const Text('Delete selected'),
                onTap: () {
                  controller.deleteSelected();
                  Navigator.pop(context);
                },
              ),
              ListTile(
                leading: const Icon(
                  Icons.copy_all_outlined,
                ),
                title: const Text('Duplicate selected'),
                onTap: () {
                  controller.duplicateSelected();
                  Navigator.pop(context);
                },
              ),
              ListTile(
                leading: const Icon(
                  Icons.format_color_fill_outlined,
                ),
                title: const Text('Background'),
                onTap: () {
                  Navigator.pop(context);
                  _showBackgroundPicker();
                },
              ),
              ListTile(
                leading: const Icon(
                  Icons.folder_open_outlined,
                ),
                title: const Text('Pick image file'),
                onTap: () async {
                  Navigator.pop(context);
                  await _pickImageFile();
                },
              ),
            ],
          ),
        );
      },
    );
  }

  Future<void> _pickImageFile() async {
    try {
      final result =
          await FilePicker.platform.pickFiles(
        type: FileType.image,
        withData: true,
      );

      if (result == null ||
          result.files.isEmpty) {
        return;
      }

      final PlatformFile file =
          result.files.first;

      final Uint8List? bytes = file.bytes;

      if (bytes == null) {
        _message('Could not read image.');
        return;
      }

      controller.addImage(bytes);
    } catch (e) {
      _message('Could not import image.');
    }
  }

  void _showBackgroundPicker() {
    const colors = [
      Colors.white,
      Color(0xFFF7F8FC),
      Color(0xFF111827),
      Color(0xFF0F172A),
      Color(0xFFEDE9FE),
      Color(0xFFFEF3C7),
      Color(0xFFDCFCE7),
      Color(0xFFFCE7F3),
    ];

    showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      builder: (context) {
        return SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Wrap(
              spacing: 14,
              runSpacing: 14,
              children: [
                for (final color in colors)
                  GestureDetector(
                    onTap: () {
                      controller.setBackground(
                        color,
                      );
                      Navigator.pop(context);
                    },
                    child: Container(
                      width: 58,
                      height: 58,
                      decoration: BoxDecoration(
                        color: color,
                        shape: BoxShape.circle,
                        border: Border.all(
                          color: Colors.black12,
                          width: 2,
                        ),
                      ),
                    ),
                  ),
              ],
            ),
          ),
        );
      },
    );
  }

  void _message(String text) {
    if (!mounted) return;

    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(
        SnackBar(
          content: Text(text),
          behavior: SnackBarBehavior.floating,
        ),
      );
  }
}
