from pathlib import Path

WS = Path('lib/screens/workspace_screen.dart')
ws = WS.read_text(encoding='utf-8')

# Make every existing bottom sheet use the same premium rounded-card surface.
if "backgroundColor: Colors.white," not in ws:
    ws = ws.replace(
        "      context: context,\n      showDragHandle:",
        "      context: context,\n      backgroundColor: Colors.white,\n      shape: RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(28))),\n      showDragHandle:",
    )
    ws = ws.replace(
        "      context: context,\n      isScrollControlled: true,\n      showDragHandle:",
        "      context: context,\n      isScrollControlled: true,\n      backgroundColor: Colors.white,\n      shape: RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(28))),\n      showDragHandle:",
    )


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

# Reference-style Composer: bottom-sheet editor instead of a generic dialog.
ws = replace_method(ws, '  Future<String?> _textDialog(String title, String initial)', r'''  Future<String?> _textDialog(String title, String initial) async {
    final textController = TextEditingController(text: initial);
    final result = await showModalBottomSheet<String>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(30))),
      showDragHandle: true,
      builder: (sheetContext) {
        return SafeArea(
          child: Padding(
            padding: EdgeInsets.fromLTRB(20, 8, 20, MediaQuery.viewInsetsOf(sheetContext).bottom + 20),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const _SheetHeader('Composer', 'Write and format Urdu text in the same premium editor style'),
                Container(
                  decoration: BoxDecoration(color: const Color(0xFFF7F7FA), borderRadius: BorderRadius.circular(20), border: Border.all(color: const Color(0xFFE5E5EA))),
                  padding: const EdgeInsets.all(12),
                  child: TextField(
                    controller: textController,
                    autofocus: true,
                    maxLines: 7,
                    textDirection: TextDirection.rtl,
                    style: const TextStyle(fontFamily: 'Gulzar', fontSize: 24, height: 1.35),
                    decoration: const InputDecoration(hintText: 'اردو متن یہاں لکھیں', border: InputBorder.none),
                  ),
                ),
                const SizedBox(height: 10),
                Row(
                  children: [
                    Expanded(child: OutlinedButton.icon(onPressed: () => Navigator.pop(sheetContext), icon: const Icon(Icons.close_rounded), label: const Text('Cancel'))),
                    const SizedBox(width: 10),
                    Expanded(child: FilledButton.icon(onPressed: () => Navigator.pop(sheetContext, textController.text), icon: const Icon(Icons.check_rounded), label: const Text('Apply'))),
                  ],
                ),
              ],
            ),
          ),
        );
      },
    );
    textController.dispose();
    return result;
  }''')

# Reference-style font browser with search + preview cards.
ws = replace_method(ws, '  Future<void> _fontSheet()', r'''  Future<void> _fontSheet() async {
    final element = controller.selected;
    if (element == null) return;
    final searchController = TextEditingController();
    final family = await showModalBottomSheet<String>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(30))),
      showDragHandle: true,
      builder: (sheetContext) {
        final fonts = [
          ('Gulzar', 'Contemporary Nastaliq', 'Gulzar'),
          ('Noto Nastaliq Urdu', 'Google Fonts Nastaliq', 'NotoNastaliqUrdu'),
          ('Mehr Nastaliq', 'Traditional Urdu preview', 'MehrNastaliq'),
          ('Alvi Nastaleeq', 'Classic Urdu display', 'AlviNastaleeq'),
          ('Jameel Noori', 'Jameel Noori Nastaleeq', 'JameelNoori'),
        ];
        return StatefulBuilder(
          builder: (context, setState) {
            final query = searchController.text.trim().toLowerCase();
            final visible = fonts.where((f) => f.$1.toLowerCase().contains(query) || f.$2.toLowerCase().contains(query)).toList();
            return SafeArea(
              child: SizedBox(
                height: MediaQuery.sizeOf(context).height * .72,
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(18, 4, 18, 18),
                  child: Column(
                    children: [
                      const _SheetHeader('Fonts', 'Search, preview and apply Urdu typography'),
                      TextField(
                        controller: searchController,
                        onChanged: (_) => setState(() {}),
                        decoration: InputDecoration(prefixIcon: const Icon(Icons.search_rounded), hintText: 'Search fonts', filled: true, fillColor: const Color(0xFFF7F7FA), border: OutlineInputBorder(borderRadius: BorderRadius.circular(18), borderSide: BorderSide.none)),
                      ),
                      const SizedBox(height: 10),
                      Expanded(
                        child: ListView.separated(
                          itemCount: visible.length,
                          separatorBuilder: (_, __) => const SizedBox(height: 8),
                          itemBuilder: (_, index) {
                            final font = visible[index];
                            final active = element.fontFamily == font.$3 || (element.fontFamily == 'JameelNoori' && font.$3 == 'Gulzar');
                            return Material(
                              color: active ? const Color(0xFFF3ECFF) : const Color(0xFFF8F8FA),
                              borderRadius: BorderRadius.circular(20),
                              child: InkWell(
                                borderRadius: BorderRadius.circular(20),
                                onTap: () => Navigator.pop(sheetContext, font.$3),
                                child: Padding(
                                  padding: const EdgeInsets.fromLTRB(16, 12, 12, 12),
                                  child: Row(
                                    children: [
                                      Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(font.$1, style: const TextStyle(fontWeight: FontWeight.w900)), const SizedBox(height: 3), Text('بِسْمِ اللّٰهِ الرَّحْمٰنِ الرَّحِيْمِ', textDirection: TextDirection.rtl, style: TextStyle(fontFamily: font.$3, fontSize: 23, color: const Color(0xFF33333A))), const SizedBox(height: 2), Text(font.$2, style: const TextStyle(fontSize: 10, color: Colors.black54))])),
                                      if (active) const Icon(Icons.check_circle_rounded, color: Color(0xFF6D28D9)),
                                    ],
                                  ),
                                ),
                              ),
                            );
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
      },
    );
    searchController.dispose();
    if (family != null) controller.setSelectedFont(family);
  }''')

# Add a premium grid background to the editor area after the demo toolbar rewrite.
if '_ReferenceGridPainter' not in ws:
    old_canvas = "                  child: ColoredBox(\n                    color: const Color(0xFFE9E9EC),\n                    child: InteractiveViewer("
    new_canvas = "                  child: CustomPaint(\n                    painter: _ReferenceGridPainter(),\n                    child: InteractiveViewer("
    if old_canvas in ws:
        ws = ws.replace(old_canvas, new_canvas, 1)
    ws += r'''

class _ReferenceGridPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    canvas.drawRect(Offset.zero & size, Paint()..color = const Color(0xFFE9E9EC));
    final paint = Paint()..color = const Color(0xFFD7D7DC)..strokeWidth = 0.7;
    const gap = 18.0;
    for (double x = 0; x <= size.width; x += gap) {
      canvas.drawLine(Offset(x, 0), Offset(x, size.height), paint);
    }
    for (double y = 0; y <= size.height; y += gap) {
      canvas.drawLine(Offset(0, y), Offset(size.width, y), paint);
    }
  }

  @override
  bool shouldRepaint(covariant _ReferenceGridPainter oldDelegate) => false;
}
'''

WS.write_text(ws, encoding='utf-8')

# Canvas quick-actions: selected object gets the same floating action language as the reference.
CANVAS = Path('lib/widgets/design_canvas.dart')
canvas = CANVAS.read_text(encoding='utf-8')
if '_quickActionBar' not in canvas:
    canvas = canvas.replace('clipBehavior: Clip.hardEdge,', 'clipBehavior: Clip.none,', 1)
    needle = "            if (selected && !e.locked) _selectionHandles(e),"
    replacement = needle + "\n            if (selected && !e.locked) _quickActionBar(e),"
    if needle not in canvas:
        raise SystemExit('selection handle insertion point not found')
    canvas = canvas.replace(needle, replacement, 1)
    insert = canvas.index('  Widget _selectionHandles(DesignElement e) {')
    quick = r'''  Widget _quickActionBar(DesignElement e) {
    return Positioned(
      left: 0,
      right: 0,
      bottom: -54 / scale,
      child: Center(
        child: Material(
          color: const Color(0xFF343442),
          elevation: 8,
          borderRadius: BorderRadius.circular(18 / scale),
          child: Padding(
            padding: EdgeInsets.symmetric(horizontal: 5 / scale, vertical: 4 / scale),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                _quickAction(Icons.open_with_rounded, 'Move', () => controller.moveSelectedBy(12, 0)),
                _quickAction(Icons.delete_outline_rounded, 'Delete', controller.deleteSelected),
                _quickAction(Icons.copy_rounded, 'Duplicate', controller.duplicateSelected),
                _quickAction(Icons.more_horiz_rounded, 'More', () => _quickMore(e)),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _quickAction(IconData icon, String tooltip, VoidCallback onTap) {
    return IconButton(
      tooltip: tooltip,
      visualDensity: VisualDensity.compact,
      padding: EdgeInsets.all(7 / scale),
      constraints: BoxConstraints(minWidth: 38 / scale, minHeight: 38 / scale),
      onPressed: onTap,
      icon: Icon(icon, color: Colors.white, size: 18 / scale),
    );
  }

  Future<void> _quickMore(DesignElement e) async {
    await showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(28))),
      builder: (sheetContext) => SafeArea(
        child: Wrap(
          children: [
            const ListTile(title: Text('Quick actions', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900))),
            ListTile(leading: const Icon(Icons.center_focus_strong_rounded), title: const Text('Center on canvas'), onTap: () { controller.centerSelected(); Navigator.pop(sheetContext); }),
            ListTile(leading: const Icon(Icons.rotate_left_rounded), title: const Text('Reset rotation'), onTap: () { controller.resetSelectedRotation(); Navigator.pop(sheetContext); }),
            ListTile(leading: const Icon(Icons.lock_outline_rounded), title: Text(e.locked ? 'Unlock' : 'Lock'), onTap: () { controller.toggleSelectedLock(); Navigator.pop(sheetContext); }),
          ],
        ),
      ),
    );
  }

'''
    canvas = canvas[:insert] + quick + canvas[insert:]
CANVAS.write_text(canvas, encoding='utf-8')

print('Applied reference-style Composer, premium sheets, canvas grid and floating quick actions.')
