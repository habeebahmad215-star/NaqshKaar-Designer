from pathlib import Path

W = Path('lib/screens/workspace_screen.dart')
w = W.read_text(encoding='utf-8')
start = w.index('  Future<void> _canvasSizeDialog()')
end = w.index('\n  Future<void> _pickImage()', start)
method = r'''  Future<void> _canvasSizeDialog() async {
    final widthController = TextEditingController(text: controller.page.size.width.round().toString());
    final heightController = TextEditingController(text: controller.page.size.height.round().toString());
    var width = controller.page.size.width;
    var height = controller.page.size.height;
    final accepted = await showModalBottomSheet<bool>(
      context: context,
      isScrollControlled: true,
      showDragHandle: true,
      backgroundColor: const Color(0xFFF7F7FA),
      builder: (sheetContext) {
        return StatefulBuilder(
          builder: (context, setSheetState) {
            void refresh() {
              setSheetState(() {
                width = (double.tryParse(widthController.text) ?? width).clamp(64, 16000).toDouble();
                height = (double.tryParse(heightController.text) ?? height).clamp(64, 16000).toDouble();
              });
            }
            final ratio = (width / height).clamp(.25, 4.0).toDouble();
            return SafeArea(
              child: Padding(
                padding: EdgeInsets.fromLTRB(18, 8, 18, 18 + MediaQuery.viewInsetsOf(context).bottom),
                child: SingleChildScrollView(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const _SheetHeader('Canvas Size', 'Live dimension preview before resizing'),
                      Container(
                        height: 130,
                        width: double.infinity,
                        alignment: Alignment.center,
                        decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(18)),
                        child: FractionallySizedBox(
                          widthFactor: ratio >= 1 ? .72 : .32,
                          heightFactor: ratio >= 1 ? .32 : .72,
                          child: Container(
                            decoration: BoxDecoration(color: const Color(0xFFF5F3FF), border: Border.all(color: _primary, width: 2), borderRadius: BorderRadius.circular(7)),
                            alignment: Alignment.center,
                            child: FittedBox(child: Text('${width.round()} × ${height.round()}', style: const TextStyle(fontWeight: FontWeight.w900))),
                          ),
                        ),
                      ),
                      const SizedBox(height: 14),
                      Row(
                        children: [
                          Expanded(child: TextField(controller: widthController, keyboardType: TextInputType.number, onChanged: (_) => refresh(), decoration: const InputDecoration(labelText: 'Width', border: OutlineInputBorder()))),
                          const SizedBox(width: 12),
                          Expanded(child: TextField(controller: heightController, keyboardType: TextInputType.number, onChanged: (_) => refresh(), decoration: const InputDecoration(labelText: 'Height', border: OutlineInputBorder()))),
                        ],
                      ),
                      const SizedBox(height: 12),
                      Row(children: [Expanded(child: OutlinedButton(onPressed: () => Navigator.pop(sheetContext, false), child: const Text('Cancel'))), const SizedBox(width: 10), Expanded(child: FilledButton(onPressed: () => Navigator.pop(sheetContext, true), child: const Text('Resize')))]),
                    ],
                  ),
                ),
              ),
            );
          },
        );
      },
    );
    if (accepted == true) {
      final width = (double.tryParse(widthController.text) ?? controller.page.size.width).clamp(64, 16000).toDouble();
      final height = (double.tryParse(heightController.text) ?? controller.page.size.height).clamp(64, 16000).toDouble();
      controller.resizeCanvas(width, height);
    }
    widthController.dispose();
    heightController.dispose();
  }
'''
w = w[:start] + method + w[end:]
W.write_text(w, encoding='utf-8')
print('Canvas size live-preview panel corrected.')
