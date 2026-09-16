from pathlib import Path

path = Path('lib/screens/workspace_screen.dart')
text = path.read_text(encoding='utf-8')

old = """        _mainTool(Icons.layers_outlined, 'Pages', _pagesSheet),
        _mainTool(Icons.tune_rounded, 'Design', _designSheet),
"""
new = """        _mainTool(Icons.layers_outlined, 'Pages', _pagesSheet),
        _mainTool(Icons.aspect_ratio_rounded, 'Paper', _paperSizeSheet),
        _mainTool(Icons.tune_rounded, 'Design', _designSheet),
"""
if old not in text:
    raise SystemExit('Main toolbar insertion point not found')
text = text.replace(old, new, 1)

marker = """  Future<void> _pickImage() async {
"""
method = r'''  Future<void> _paperSizeSheet() async {
    final presets = <_PaperPreset>[
      const _PaperPreset('A4', '210 × 297 mm', 2480, 3508, Icons.description_outlined),
      const _PaperPreset('A4 Landscape', '297 × 210 mm', 3508, 2480, Icons.stay_current_landscape_outlined),
      const _PaperPreset('A5', '148 × 210 mm', 1748, 2480, Icons.description_outlined),
      const _PaperPreset('A5 Landscape', '210 × 148 mm', 2480, 1748, Icons.stay_current_landscape_outlined),
      const _PaperPreset('Letter', '8.5 × 11 in', 2550, 3300, Icons.article_outlined),
      const _PaperPreset('Letter Landscape', '11 × 8.5 in', 3300, 2550, Icons.stay_current_landscape_outlined),
      const _PaperPreset('Legal', '8.5 × 14 in', 2550, 4200, Icons.description_outlined),
      const _PaperPreset('Legal Landscape', '14 × 8.5 in', 4200, 2550, Icons.stay_current_landscape_outlined),
      const _PaperPreset('Square', '1 : 1', 1080, 1080, Icons.crop_square_rounded),
      const _PaperPreset('Instagram Post', '4 : 5', 1080, 1350, Icons.photo_outlined),
      const _PaperPreset('Instagram Story', '9 : 16', 1080, 1920, Icons.phone_android_outlined),
      const _PaperPreset('YouTube', '16 : 9', 1920, 1080, Icons.ondemand_video_outlined),
    ];

    await showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      showDragHandle: true,
      builder: (sheetContext) {
        return SafeArea(
          child: SizedBox(
            height: MediaQuery.sizeOf(context).height * .82,
            child: Column(
              children: [
                const _SheetHeader('Resize Paper', 'Change the artboard anytime without leaving your design'),
                Padding(
                  padding: const EdgeInsets.fromLTRB(20, 0, 20, 8),
                  child: Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: _primary.withValues(alpha: .07),
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: _primary.withValues(alpha: .16)),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.aspect_ratio_rounded, color: _primary),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Text(
                            'Current  ${controller.page.size.width.round()} × ${controller.page.size.height.round()} px',
                            style: const TextStyle(fontWeight: FontWeight.w800),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                Expanded(
                  child: ListView.separated(
                    padding: const EdgeInsets.fromLTRB(16, 4, 16, 18),
                    itemCount: presets.length + 1,
                    separatorBuilder: (_, __) => const SizedBox(height: 7),
                    itemBuilder: (context, index) {
                      if (index == presets.length) {
                        return Card(
                          elevation: 0,
                          child: ListTile(
                            leading: const CircleAvatar(child: Icon(Icons.edit_rounded)),
                            title: const Text('Custom size', style: TextStyle(fontWeight: FontWeight.w900)),
                            subtitle: const Text('Enter exact width and height in pixels'),
                            trailing: const Icon(Icons.chevron_right_rounded),
                            onTap: () async {
                              Navigator.pop(sheetContext);
                              await _customPaperSizeDialog();
                            },
                          ),
                        );
                      }
                      final preset = presets[index];
                      final active = controller.page.size.width.round() == preset.width && controller.page.size.height.round() == preset.height;
                      return Card(
                        elevation: 0,
                        child: ListTile(
                          leading: CircleAvatar(
                            backgroundColor: active ? _primary : _primary.withValues(alpha: .08),
                            child: Icon(preset.icon, color: active ? Colors.white : _primary),
                          ),
                          title: Text(preset.name, style: const TextStyle(fontWeight: FontWeight.w900)),
                          subtitle: Text('${preset.label}  •  ${preset.width} × ${preset.height} px'),
                          trailing: active ? const Icon(Icons.check_circle_rounded, color: _primary) : const Icon(Icons.chevron_right_rounded),
                          onTap: () {
                            controller.resizeCanvas(preset.width.toDouble(), preset.height.toDouble());
                            Navigator.pop(sheetContext);
                          },
                        ),
                      );
                    },
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Future<void> _customPaperSizeDialog() async {
    final widthController = TextEditingController(text: controller.page.size.width.round().toString());
    final heightController = TextEditingController(text: controller.page.size.height.round().toString());
    final accepted = await showDialog<bool>(
      context: context,
      builder: (dialogContext) {
        return AlertDialog(
          title: const Text('Custom Paper Size', style: TextStyle(fontWeight: FontWeight.w900)),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Align(alignment: Alignment.centerLeft, child: Text('Exact artboard dimensions', style: TextStyle(color: Colors.black54))),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(child: TextField(controller: widthController, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Width', suffixText: 'px'))),
                  const SizedBox(width: 12),
                  Expanded(child: TextField(controller: heightController, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Height', suffixText: 'px'))),
                ],
              ),
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
      final width = (double.tryParse(widthController.text) ?? controller.page.size.width).clamp(64, 16000).toDouble();
      final height = (double.tryParse(heightController.text) ?? controller.page.size.height).clamp(64, 16000).toDouble();
      controller.resizeCanvas(width, height);
    }
    widthController.dispose();
    heightController.dispose();
  }

'''
if marker not in text:
    raise SystemExit('Paper method insertion marker not found')
text = text.replace(marker, method + marker, 1)

text += r'''

class _PaperPreset {
  final String name;
  final String label;
  final int width;
  final int height;
  final IconData icon;
  const _PaperPreset(this.name, this.label, this.width, this.height, this.icon);
}
'''
path.write_text(text, encoding='utf-8')
print('Applied smart paper resize UI')
