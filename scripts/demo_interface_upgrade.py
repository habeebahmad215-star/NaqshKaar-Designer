from pathlib import Path

PATH = Path('lib/screens/workspace_screen.dart')
text = PATH.read_text(encoding='utf-8')

if "../widgets/layers_panel.dart" not in text:
    text = text.replace("import '../widgets/design_canvas.dart';", "import '../widgets/design_canvas.dart';\nimport '../widgets/layers_panel.dart';")


def replace_method(source: str, signature: str, replacement: str) -> str:
    start = source.index(signature)
    brace = source.index('{', start)
    depth = 0
    end = None
    for i in range(brace, len(source)):
        ch = source[i]
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end is None:
        raise SystemExit(f'Could not close method: {signature}')
    return source[:start] + replacement.rstrip() + source[end:]


text = replace_method(text, '  PreferredSizeWidget _buildAppBar()', r'''  PreferredSizeWidget _buildAppBar() {
    return PreferredSize(
      preferredSize: const Size.fromHeight(78),
      child: SafeArea(
        bottom: false,
        child: Padding(
          padding: const EdgeInsets.fromLTRB(12, 10, 12, 8),
          child: Material(
            color: Colors.white,
            elevation: 7,
            shadowColor: Colors.black26,
            borderRadius: BorderRadius.circular(24),
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
              child: Row(
                children: [
                  _topAction(Icons.menu_rounded, 'Menu', () => _designSheet()),
                  _topAction(Icons.layers_rounded, 'Layers', _showLayersSheet),
                  _topAction(Icons.align_horizontal_center_rounded, 'Align', _showAlignSheet),
                  _topAction(Icons.open_with_rounded, 'Move', _showMoveSheet),
                  _topAction(Icons.undo_rounded, 'Undo', controller.canUndo ? controller.undo : null),
                  _topAction(Icons.redo_rounded, 'Redo', controller.canRedo ? controller.redo : null),
                  const Spacer(),
                  Material(
                    color: const Color(0xFF6D28D9),
                    borderRadius: BorderRadius.circular(17),
                    child: InkWell(
                      borderRadius: BorderRadius.circular(17),
                      onTap: _save,
                      child: const Padding(
                        padding: EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(Icons.save_rounded, color: Colors.white, size: 22),
                            SizedBox(height: 1),
                            Text('Save', style: TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.w900)),
                          ],
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _topAction(IconData icon, String label, VoidCallback? onTap) {
    final active = onTap != null;
    return SizedBox(
      width: 58,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(15),
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 3),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(icon, size: 23, color: active ? const Color(0xFF4B4B55) : const Color(0xFFBDBDC3)),
              const SizedBox(height: 2),
              Text(label, maxLines: 1, overflow: TextOverflow.ellipsis, style: TextStyle(fontSize: 9, fontWeight: FontWeight.w800, color: active ? const Color(0xFF66666F) : const Color(0xFFBDBDC3))),
            ],
          ),
        ),
      ),
    );
  }''')

text = replace_method(text, '  Widget _buildCanvasArea()', r'''  Widget _buildCanvasArea() {
    return LayoutBuilder(
      builder: (context, constraints) {
        final availableWidth = (constraints.maxWidth - 30).clamp(120.0, double.infinity).toDouble();
        final availableHeight = (constraints.maxHeight - 30).clamp(120.0, double.infinity).toDouble();
        final widthScale = availableWidth / controller.page.size.width;
        final heightScale = availableHeight / controller.page.size.height;
        final fitScale = (widthScale < heightScale ? widthScale : heightScale).clamp(0.05, 1.0).toDouble();
        return AnimatedBuilder(
          animation: _transform,
          builder: (context, child) {
            final zoom = _transform.value.getMaxScaleOnAxis().clamp(0.5, 4.0).toDouble();
            return Stack(
              children: [
                Positioned.fill(
                  child: ColoredBox(
                    color: const Color(0xFFE9E9EC),
                    child: InteractiveViewer(
                      transformationController: _transform,
                      minScale: 0.5,
                      maxScale: 4,
                      constrained: false,
                      boundaryMargin: const EdgeInsets.all(260),
                      child: Center(
                        child: SizedBox(
                          width: availableWidth,
                          height: availableHeight,
                          child: FittedBox(
                            fit: BoxFit.contain,
                            child: Container(
                              decoration: const BoxDecoration(boxShadow: [BoxShadow(blurRadius: 22, offset: Offset(0, 10), color: Color(0x33000000))]),
                              child: DesignCanvas(controller: controller, repaintKey: _canvasKey, interactionScale: fitScale * zoom),
                            ),
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
                Positioned(top: 10, left: 12, child: _darkPill(Icons.lock_outline_rounded, 'Lock', controller.toggleSelectedLock)),
                Positioned(top: 10, right: 12, child: _darkPill(Icons.fullscreen_rounded, 'Reset Zoom', () => _transform.value = Matrix4.identity())),
                Positioned(left: 12, bottom: 10, child: _zoomBadge(zoom)),
              ],
            );
          },
        );
      },
    );
  }

  Widget _darkPill(IconData icon, String label, VoidCallback onTap) {
    return Material(
      color: const Color(0xFF3D3D50),
      elevation: 5,
      borderRadius: BorderRadius.circular(17),
      child: InkWell(
        borderRadius: BorderRadius.circular(17),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 13, vertical: 10),
          child: Row(children: [Icon(icon, color: Colors.white, size: 19), const SizedBox(width: 6), Text(label, style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.w900))]),
        ),
      ),
    );
  }

  Widget _zoomBadge(double zoom) {
    return Material(
      color: Colors.white,
      elevation: 4,
      borderRadius: BorderRadius.circular(15),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 11, vertical: 7),
        child: Text('${(zoom * 100).round()}%', style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w900)),
      ),
    );
  }''')

text = replace_method(text, '  Widget _buildToolbar()', r'''  Widget _buildToolbar() {
    return SafeArea(
      top: false,
      child: Container(
        decoration: const BoxDecoration(
          color: Color(0xFFF8F8FA),
          boxShadow: [BoxShadow(blurRadius: 20, offset: Offset(0, -7), color: Color(0x26000000))],
        ),
        child: controller.selected == null ? _mainToolbar() : _selectedToolbar(controller.selected!),
      ),
    );
  }''')

text = replace_method(text, '  Widget _mainToolbar()', r'''  Widget _mainToolbar() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(8, 8, 8, 10),
      child: Row(
        children: [
          _bottomTool(Icons.text_fields_rounded, 'Text', _addText),
          _bottomTool(Icons.crop_square_rounded, 'Shape', controller.addShape),
          _bottomTool(Icons.add_photo_alternate_outlined, 'Image', _pickImage),
          _bottomTool(Icons.layers_outlined, 'Pages', _pagesSheet),
          _bottomTool(Icons.palette_outlined, 'Background', _backgroundSheet),
          _bottomTool(Icons.more_horiz_rounded, 'More', _designSheet),
        ],
      ),
    );
  }

  Widget _bottomTool(IconData icon, String label, VoidCallback onTap, {bool active = false}) {
    return Expanded(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(14),
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 5),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(icon, size: 23, color: active ? const Color(0xFF6D28D9) : const Color(0xFF68686F)),
              const SizedBox(height: 4),
              Text(label, maxLines: 1, overflow: TextOverflow.ellipsis, style: TextStyle(fontSize: 9, fontWeight: FontWeight.w800, color: active ? const Color(0xFF6D28D9) : const Color(0xFF5F5F66))),
            ],
          ),
        ),
      ),
    );
  }''')

text = replace_method(text, '  Widget _selectedToolbar(DesignElement element)', r'''  Widget _selectedToolbar(DesignElement element) {
    final isText = element.kind == ElementKind.text;
    final first = <Widget>[
      _bottomTool(Icons.delete_outline_rounded, 'Delete', controller.deleteSelected),
      if (isText) _bottomTool(Icons.format_size_rounded, 'Resize', () => _fontSize(element)),
      if (!isText) _bottomTool(Icons.open_with_rounded, 'Resize', _showMoveSheet),
      _bottomTool(Icons.border_color_outlined, 'Border', _effectsSheet),
      _bottomTool(Icons.wb_sunny_outlined, 'Shadow', _effectsSheet),
      _bottomTool(Icons.copy_rounded, 'Duplicate', controller.duplicateSelected),
      _bottomTool(Icons.opacity_rounded, 'Opacity', _opacity),
    ];
    final second = <Widget>[
      _bottomTool(Icons.remove_circle_outline_rounded, 'Deselect', () => controller.select(null), active: true),
      if (isText) _bottomTool(Icons.font_download_outlined, 'Font', _fontSheet),
      _bottomTool(Icons.palette_outlined, 'Color', _colorSheet),
      _bottomTool(Icons.auto_awesome_rounded, 'Effects', _effectsSheet),
      if (isText) _bottomTool(Icons.translate_rounded, 'RTL / LTR', _directionSheet),
      _bottomTool(Icons.more_horiz_rounded, 'More', _moreSheet),
    ];
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        _toolStrip(first),
        const Divider(height: 1),
        _toolStrip(second),
      ],
    );
  }

  Widget _toolStrip(List<Widget> tools) {
    return SizedBox(
      height: 68,
      child: Row(children: tools),
    );
  }''')

insert_at = text.index('  Future<void> _addText()')
helpers = r'''
  Future<void> _showLayersSheet() async {
    await showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      showDragHandle: true,
      backgroundColor: const Color(0xFFF7F7FA),
      builder: (_) => SizedBox(height: MediaQuery.sizeOf(context).height * .72, child: LayersPanel(controller: controller)),
    );
  }

  Future<void> _showAlignSheet() async {
    final element = controller.selected;
    if (element == null) return;
    await showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      builder: (sheetContext) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(18, 8, 18, 24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const _SheetHeader('Align & Arrange', 'Snap the selected object precisely on the canvas'),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  _choiceAction(Icons.align_horizontal_left_rounded, 'Left', () { controller.updateSelected(x: 0); Navigator.pop(sheetContext); }),
                  _choiceAction(Icons.align_horizontal_center_rounded, 'Center', () { controller.centerSelected(); Navigator.pop(sheetContext); }),
                  _choiceAction(Icons.align_horizontal_right_rounded, 'Right', () { controller.updateSelected(x: controller.page.size.width - element.width); Navigator.pop(sheetContext); }),
                  _choiceAction(Icons.vertical_align_top_rounded, 'Top', () { controller.updateSelected(y: 0); Navigator.pop(sheetContext); }),
                  _choiceAction(Icons.vertical_align_center_rounded, 'Middle', () { controller.updateSelected(y: (controller.page.size.height - element.height) / 2); Navigator.pop(sheetContext); }),
                  _choiceAction(Icons.vertical_align_bottom_rounded, 'Bottom', () { controller.updateSelected(y: controller.page.size.height - element.height); Navigator.pop(sheetContext); }),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _choiceAction(IconData icon, String label, VoidCallback onTap) {
    return SizedBox(
      width: 104,
      child: OutlinedButton.icon(onPressed: onTap, icon: Icon(icon, size: 18), label: Text(label, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800))),
    );
  }

  Future<void> _showMoveSheet() async {
    if (controller.selected == null) return;
    const step = 12.0;
    await showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      builder: (sheetContext) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(18, 6, 18, 22),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Row(children: [const Icon(Icons.open_with_rounded), const SizedBox(width: 10), const Expanded(child: Text('Move', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w900))), IconButton(onPressed: () => Navigator.pop(sheetContext), icon: const Icon(Icons.close_rounded))]),
              const SizedBox(height: 8),
              GridView.count(
                crossAxisCount: 3,
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                childAspectRatio: 1.35,
                children: [
                  _moveKey(Icons.north_west_rounded, -step, -step), _moveKey(Icons.keyboard_arrow_up_rounded, 0, -step), _moveKey(Icons.north_east_rounded, step, -step),
                  _moveKey(Icons.keyboard_arrow_left_rounded, -step, 0), _moveKey(Icons.center_focus_strong_rounded, 0, 0, center: true), _moveKey(Icons.keyboard_arrow_right_rounded, step, 0),
                  _moveKey(Icons.south_west_rounded, -step, step), _moveKey(Icons.keyboard_arrow_down_rounded, 0, step), _moveKey(Icons.south_east_rounded, step, step),
                ],
              ),
              const Divider(),
              Row(children: [Expanded(child: OutlinedButton.icon(onPressed: () { controller.updateSelected(rotation: controller.selected!.rotation - 0.0872665); }, icon: const Icon(Icons.rotate_left_rounded), label: const Text('Rotate'))), const SizedBox(width: 10), Expanded(child: OutlinedButton.icon(onPressed: () { controller.updateSelected(rotation: controller.selected!.rotation + 0.0872665); }, icon: const Icon(Icons.rotate_right_rounded), label: const Text('Rotate')))]),
            ],
          ),
        ),
      ),
    );
  }

  Widget _moveKey(IconData icon, double dx, double dy, {bool center = false}) {
    return InkWell(
      onTap: () { if (center) { controller.centerSelected(); } else { controller.moveSelectedBy(dx, dy); } },
      borderRadius: BorderRadius.circular(12),
      child: Center(child: Icon(icon, size: 28, color: const Color(0xFF77777F))),
    );
  }

'''
text = text[:insert_at] + helpers + text[insert_at:]

PATH.write_text(text, encoding='utf-8')
print('Applied demo-inspired premium editor chrome.')
