from pathlib import Path

PATH = Path('lib/screens/workspace_screen.dart')
text = PATH.read_text(encoding='utf-8')


def replace_method(source: str, signature: str, replacement: str) -> str:
    start = source.index(signature)
    brace = source.index('{', start)
    depth = 0
    for i in range(brace, len(source)):
        ch = source[i]
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return source[:start] + replacement.rstrip() + source[i + 1:]
    raise SystemExit(f'Could not close method: {signature}')


text = replace_method(text, '  Widget _mainToolbar()', r'''  Widget _mainToolbar() {
    return Container(
      padding: const EdgeInsets.fromLTRB(8, 6, 8, 8),
      decoration: const BoxDecoration(color: Color(0xFFF7F7FA)),
      child: Row(
        children: [
          _utilityTool(Icons.add_rounded, 'ADD NEW', _addNewSheet, active: true),
          _utilityTool(Icons.fullscreen_rounded, 'Resize Paper', _resizePaperSheet),
          _utilityTool(Icons.circle_outlined, 'Transparent BG', _transparentBackground),
          _utilityTool(Icons.format_color_fill_rounded, 'BG Color', _backgroundSheet),
          _utilityTool(Icons.video_library_outlined, 'Timeline', _timelineSheet),
        ],
      ),
    );
  }

  Widget _utilityTool(IconData icon, String label, VoidCallback onTap, {bool active = false}) {
    return Expanded(
      child: Material(
        color: active ? const Color(0xFFEDE3FF) : Colors.transparent,
        borderRadius: BorderRadius.circular(16),
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(16),
          child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 7, horizontal: 2),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(icon, size: 23, color: active ? const Color(0xFF6D28D9) : const Color(0xFF6B6B73)),
                const SizedBox(height: 3),
                Text(label, maxLines: 1, overflow: TextOverflow.ellipsis, style: TextStyle(fontSize: 8.5, fontWeight: FontWeight.w900, color: active ? const Color(0xFF5B21B6) : const Color(0xFF62626A))),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Future<void> _addNewSheet() async {
    await showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      showDragHandle: true,
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(30))),
      builder: (sheetContext) {
        final items = <_AddNewItem>[
          _AddNewItem(Icons.photo_library_rounded, 'Gallery Pic', 'Add photo', _pickImage, const Color(0xFF2563EB)),
          _AddNewItem(Icons.collections_rounded, 'Stock Images', 'Browse stock', _designSheet, const Color(0xFF5B5BEF)),
          _AddNewItem(Icons.folder_rounded, 'My Folder', 'Your files', _pickImage, const Color(0xFF0EA5A8)),
          _AddNewItem(Icons.text_fields_rounded, 'Add Text', 'Urdu composer', _addText, const Color(0xFFF97316)),
          _AddNewItem(Icons.video_library_rounded, 'Video', 'Add video', _timelineSheet, const Color(0xFFE11D48)),
          _AddNewItem(Icons.music_note_rounded, 'Audio', 'Add audio', _timelineSheet, const Color(0xFF059669)),
          _AddNewItem(Icons.auto_awesome_rounded, 'AI Images', 'AI tools', _designSheet, const Color(0xFF7C3AED)),
          _AddNewItem(Icons.build_rounded, 'Tools', 'Design tools', _designSheet, const Color(0xFF475569)),
          _AddNewItem(Icons.crop_square_rounded, 'Borders', 'Border styles', _effectsSheet, const Color(0xFFF59E0B)),
          _AddNewItem(Icons.grid_view_rounded, 'Table', 'Grid/table', _designSheet, const Color(0xFF0D9488)),
          _AddNewItem(Icons.brush_rounded, 'Draw', 'Freehand', _designSheet, const Color(0xFFE11D48)),
          _AddNewItem(Icons.edit_rounded, 'Pen Tool', 'Precision draw', _designSheet, const Color(0xFF7C3AED)),
          _AddNewItem(Icons.business_rounded, 'Logos', 'Brand marks', _designSheet, const Color(0xFF0D9488)),
          _AddNewItem(Icons.gesture_rounded, 'Special Text', 'Stylish text', _addText, const Color(0xFF0D9488)),
          _AddNewItem(Icons.category_rounded, 'Shapes', 'Vector shapes', controller.addShape, const Color(0xFF0D9488)),
          _AddNewItem(Icons.star_rounded, 'PNG Images', 'Transparent PNG', _pickImage, const Color(0xFF2563EB)),
          _AddNewItem(Icons.wallpaper_rounded, 'Backgrounds', 'Canvas background', _backgroundSheet, const Color(0xFF2563EB)),
        ];
        return SafeArea(
          child: SizedBox(
            height: MediaQuery.sizeOf(sheetContext).height * .82,
            child: Padding(
              padding: const EdgeInsets.fromLTRB(14, 2, 14, 14),
              child: Column(
                children: [
                  Row(
                    children: [
                      const Expanded(child: _SheetHeader('Add New', 'Everything you need to build a premium design')),
                      IconButton(onPressed: () => Navigator.pop(sheetContext), icon: const Icon(Icons.close_rounded)),
                    ],
                  ),
                  const SizedBox(height: 6),
                  Expanded(
                    child: GridView.builder(
                      padding: const EdgeInsets.only(bottom: 8),
                      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount: 3, crossAxisSpacing: 10, mainAxisSpacing: 10, childAspectRatio: .95),
                      itemCount: items.length,
                      itemBuilder: (_, index) {
                        final item = items[index];
                        return _addNewCard(item, sheetContext);
                      },
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

  Widget _addNewCard(_AddNewItem item, BuildContext sheetContext) {
    return Material(
      color: const Color(0xFFF6F6F9),
      borderRadius: BorderRadius.circular(20),
      child: InkWell(
        onTap: () {
          Navigator.pop(sheetContext);
          item.action();
        },
        borderRadius: BorderRadius.circular(20),
        child: Padding(
          padding: const EdgeInsets.fromLTRB(8, 12, 8, 8),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                width: 62,
                height: 62,
                decoration: BoxDecoration(color: item.color, borderRadius: BorderRadius.circular(19), boxShadow: const [BoxShadow(blurRadius: 7, offset: Offset(0, 3), color: Color(0x18000000))]),
                child: Icon(item.icon, color: Colors.white, size: 31),
              ),
              const SizedBox(height: 8),
              Text(item.title, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w900)),
              const SizedBox(height: 2),
              Text(item.subtitle, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 8.5, color: Colors.black54, fontWeight: FontWeight.w600)),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _resizePaperSheet() async {
    final width = TextEditingController(text: controller.page.size.width.round().toString());
    final height = TextEditingController(text: controller.page.size.height.round().toString());
    await showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(28))),
      builder: (sheetContext) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(18, 8, 18, 24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const _SheetHeader('Resize Paper', 'Set an exact canvas size'),
              Row(children: [Expanded(child: TextField(controller: width, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Width'))), const SizedBox(width: 12), Expanded(child: TextField(controller: height, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Height')))]),
              const SizedBox(height: 14),
              SizedBox(width: double.infinity, child: FilledButton.icon(onPressed: () { final w = double.tryParse(width.text); final h = double.tryParse(height.text); if (w != null && h != null) controller.resizeCanvas(w, h); Navigator.pop(sheetContext); }, icon: const Icon(Icons.check_rounded), label: const Text('Apply Size'))),
            ],
          ),
        ),
      ),
    );
    width.dispose();
    height.dispose();
  }

  void _transparentBackground() {
    controller.setBackground(Colors.transparent);
  }

  Future<void> _timelineSheet() async {
    await showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      builder: (sheetContext) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(18, 8, 18, 22),
          child: Column(mainAxisSize: MainAxisSize.min, children: [
            const _SheetHeader('Timeline', 'Video and audio controls'),
            ListTile(leading: const Icon(Icons.video_library_rounded), title: const Text('Video track'), subtitle: const Text('Ready for timeline media tools'), onTap: () => Navigator.pop(sheetContext)),
            ListTile(leading: const Icon(Icons.music_note_rounded), title: const Text('Audio track'), subtitle: const Text('Ready for audio tools'), onTap: () => Navigator.pop(sheetContext)),
          ]),
        ),
      ),
    );
  }

  
''')

text += r'''

class _AddNewItem {
  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback action;
  final Color color;

  const _AddNewItem(this.icon, this.title, this.subtitle, this.action, this.color);
}
'''

PATH.write_text(text, encoding='utf-8')
print('Applied reference-style Add New panel and utility bar.')
