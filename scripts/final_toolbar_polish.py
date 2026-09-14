from pathlib import Path
import re

path = Path('lib/screens/workspace_screen.dart')
text = path.read_text()

appbar = r'''  PreferredSizeWidget _buildAppBar() {
    return AppBar(
      toolbarHeight: 62,
      backgroundColor: Colors.white,
      surfaceTintColor: Colors.white,
      elevation: 0,
      scrolledUnderElevation: 0.5,
      leadingWidth: 56,
      leading: Padding(
        padding: const EdgeInsets.all(8),
        child: _headerButton(Icons.arrow_back_rounded, 'Back', () => Navigator.pop(context)),
      ),
      titleSpacing: 2,
      title: Row(
        children: [
          Container(
            width: 38,
            height: 38,
            decoration: BoxDecoration(
              gradient: const LinearGradient(colors: [Color(0xFF7C3AED), Color(0xFF4F46E5)]),
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Icon(Icons.auto_awesome_rounded, color: Colors.white, size: 20),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(controller.project.name, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w900)),
                const SizedBox(height: 2),
                Text('Page ${controller.currentPageIndex + 1}  •  ${controller.page.size.width.round()} × ${controller.page.size.height.round()}', style: const TextStyle(fontSize: 9.5, color: Colors.black54, fontWeight: FontWeight.w600)),
              ],
            ),
          ),
        ],
      ),
      actions: [
        _headerButton(Icons.undo_rounded, 'Undo', controller.canUndo ? controller.undo : null),
        _headerButton(Icons.redo_rounded, 'Redo', controller.canRedo ? controller.redo : null),
        _headerButton(Icons.save_outlined, 'Save', _save),
        Padding(
          padding: const EdgeInsets.only(right: 8, left: 2),
          child: PopupMenuButton<String>(
            tooltip: 'Export design',
            onSelected: _exportMenu,
            position: PopupMenuPosition.under,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 11, vertical: 9),
              decoration: BoxDecoration(
                gradient: const LinearGradient(colors: [Color(0xFF7C3AED), Color(0xFF5B21B6)]),
                borderRadius: BorderRadius.circular(13),
                boxShadow: const [BoxShadow(blurRadius: 8, offset: Offset(0, 3), color: Color(0x22000000))],
              ),
              child: const Row(mainAxisSize: MainAxisSize.min, children: [
                Icon(Icons.ios_share_rounded, color: Colors.white, size: 17),
                SizedBox(width: 5),
                Text('Export', style: TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.w900)),
                SizedBox(width: 2),
                Icon(Icons.keyboard_arrow_down_rounded, color: Colors.white, size: 15),
              ]),
            ),
            itemBuilder: (context) => const [
              PopupMenuItem(value: 'png', child: ListTile(leading: Icon(Icons.image_outlined), title: Text('Export PNG'), dense: true)),
              PopupMenuItem(value: 'jpg', child: ListTile(leading: Icon(Icons.photo_outlined), title: Text('Export JPG'), dense: true)),
              PopupMenuItem(value: 'pdf', child: ListTile(leading: Icon(Icons.picture_as_pdf_outlined), title: Text('Share PDF'), dense: true)),
            ],
          ),
        ),
      ],
    );
  }

  Widget _headerButton(IconData icon, String tooltip, VoidCallback? onTap) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 1),
      child: IconButton(
        tooltip: tooltip,
        onPressed: onTap,
        style: IconButton.styleFrom(
          backgroundColor: onTap == null ? Colors.transparent : const Color(0xFFF4F1FA),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
        icon: Icon(icon, size: 19),
      ),
    );
  }
'''

toolbar = r'''  Widget _buildToolbar() {
    return SafeArea(
      top: false,
      child: Container(
        padding: const EdgeInsets.fromLTRB(8, 7, 8, 8),
        decoration: const BoxDecoration(
          color: Colors.white,
          boxShadow: [BoxShadow(blurRadius: 20, offset: Offset(0, -5), color: Color(0x18000000))],
        ),
        child: controller.selected == null ? _mainToolbar() : _selectedToolbar(controller.selected!),
      ),
    );
  }

  Widget _mainToolbar() {
    return SizedBox(
      height: 64,
      child: Row(
        children: [
          _mainTool(Icons.text_fields_rounded, 'Text', _addText, primary: true),
          _mainTool(Icons.crop_square_rounded, 'Shape', controller.addShape),
          _mainTool(Icons.image_outlined, 'Image', _pickImage),
          _mainTool(Icons.layers_outlined, 'Pages', _pagesSheet),
          _mainTool(Icons.tune_rounded, 'Design', _designSheet),
        ],
      ),
    );
  }

  Widget _mainTool(IconData icon, String label, VoidCallback onTap, {bool primary = false}) {
    return Expanded(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 2),
        child: Material(
          color: primary ? const Color(0xFFF3EEFF) : Colors.transparent,
          borderRadius: BorderRadius.circular(14),
          child: InkWell(
            onTap: onTap,
            borderRadius: BorderRadius.circular(14),
            child: Padding(
              padding: const EdgeInsets.symmetric(vertical: 6),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(icon, color: primary ? _primary : Colors.black87, size: 23),
                  const SizedBox(height: 3),
                  Text(label, style: TextStyle(fontSize: 10.5, fontWeight: FontWeight.w800, color: primary ? _primary : Colors.black87)),
                ],
              ),
            ),
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
        SizedBox(height: 58, child: ListView(scrollDirection: Axis.horizontal, padding: const EdgeInsets.symmetric(horizontal: 2), children: tools)),
        Container(
          margin: const EdgeInsets.only(top: 2),
          padding: const EdgeInsets.only(left: 9),
          decoration: BoxDecoration(color: const Color(0xFFF8F7FB), borderRadius: BorderRadius.circular(14)),
          child: Row(
            children: [
              Container(width: 7, height: 7, decoration: const BoxDecoration(color: _primary, shape: BoxShape.circle)),
              const SizedBox(width: 7),
              Expanded(child: Text(_elementLabel(element), maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 10.5, fontWeight: FontWeight.w800))),
              _quickAction(Icons.copy_outlined, 'Duplicate', controller.duplicateSelected),
              _quickAction(element.locked ? Icons.lock_rounded : Icons.lock_open_rounded, element.locked ? 'Unlock' : 'Lock', controller.toggleSelectedLock),
              _quickAction(Icons.delete_outline_rounded, 'Delete', controller.deleteSelected, danger: true),
            ],
          ),
        ),
      ],
    );
  }

  Widget _quickAction(IconData icon, String tooltip, VoidCallback onTap, {bool danger = false}) {
    return IconButton(
      tooltip: tooltip,
      visualDensity: VisualDensity.compact,
      onPressed: onTap,
      icon: Icon(icon, size: 19, color: danger ? Colors.red.shade700 : Colors.black87),
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
      padding: const EdgeInsets.symmetric(horizontal: 2),
      child: Material(
        color: Colors.transparent,
        borderRadius: BorderRadius.circular(12),
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(12),
          child: SizedBox(
            width: 64,
            child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
              Icon(icon, color: _primary, size: 21),
              const SizedBox(height: 3),
              Text(label, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 9, fontWeight: FontWeight.w800)),
            ]),
          ),
        ),
      ),
    );
  }

  Widget _toggleTool(IconData icon, String label, bool active, VoidCallback onTap) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 2),
      child: Material(
        color: active ? const Color(0xFFF0E9FF) : Colors.transparent,
        borderRadius: BorderRadius.circular(12),
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(12),
          child: SizedBox(
            width: 64,
            child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
              Icon(icon, color: active ? _primary : Colors.black54, size: 21),
              const SizedBox(height: 3),
              Text(label, style: TextStyle(fontSize: 9, fontWeight: FontWeight.w800, color: active ? _primary : Colors.black87)),
            ]),
          ),
        ),
      ),
    );
  }

  Future<void> _addText() async {
'''

text, n1 = re.subn(r"  PreferredSizeWidget _buildAppBar\(\) \{.*?\n  \}\n\n  Widget _buildCanvasArea", appbar + "\n  Widget _buildCanvasArea", text, count=1, flags=re.S)
if n1 != 1:
    raise SystemExit('AppBar block was not found')
text, n2 = re.subn(r"  Widget _buildToolbar\(\) \{.*?\n  Future<void> _addText\(\) async \{", toolbar, text, count=1, flags=re.S)
if n2 != 1:
    raise SystemExit('Toolbar block was not found')
path.write_text(text)
print('Toolbar polish applied successfully')
