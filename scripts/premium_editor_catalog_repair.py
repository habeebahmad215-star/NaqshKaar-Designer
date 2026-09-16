from pathlib import Path

p = Path('lib/screens/workspace_screen.dart')
s = p.read_text(encoding='utf-8')

# The catalog pass is intentionally repaired here before dart format/analyze.
start = s.find('  Future<void> _pagesSheet() async {')
end = s.find('  Future<void> _designSheet() async {', start)
if start == -1 or end == -1:
    raise SystemExit('pages sheet anchors missing')

new_pages = '''  Future<void> _pagesSheet() async {
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
                const _SheetHeader('Pages', 'Multi-page project workspace'),
                Expanded(
                  child: ListView.builder(
                    itemCount: controller.project.pages.length,
                    itemBuilder: (context, index) {
                      final selected = index == controller.currentPageIndex;
                      return ListTile(
                        leading: CircleAvatar(
                          backgroundColor: selected ? _primary : Colors.black12,
                          child: Text('${index + 1}', style: TextStyle(color: selected ? Colors.white : Colors.black87)),
                        ),
                        title: Text(controller.project.pages[index].title),
                        subtitle: Text('${controller.project.pages[index].size.width.round()} × ${controller.project.pages[index].size.height.round()}'),
                        trailing: selected ? const Icon(Icons.check_circle_rounded, color: _primary) : null,
                        onTap: () {
                          controller.switchPage(index);
                          Navigator.pop(sheetContext);
                        },
                      );
                    },
                  ),
                ),
                const Divider(height: 1),
                Padding(
                  padding: const EdgeInsets.fromLTRB(16, 8, 16, 10),
                  child: Row(
                    children: [
                      Expanded(
                        child: FilledButton.icon(
                          onPressed: () {
                            controller.addPage();
                            Navigator.pop(sheetContext);
                          },
                          icon: const Icon(Icons.add_rounded),
                          label: const Text('Add Page'),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: controller.project.pages.length > 1
                              ? () {
                                  controller.duplicatePage();
                                  Navigator.pop(sheetContext);
                                }
                              : null,
                          icon: const Icon(Icons.copy_all_outlined),
                          label: const Text('Duplicate'),
                        ),
                      ),
                      const SizedBox(width: 4),
                      IconButton(
                        tooltip: 'Delete page',
                        onPressed: controller.project.pages.length > 1
                            ? () {
                                controller.deletePage();
                                Navigator.pop(sheetContext);
                              }
                            : null,
                        icon: const Icon(Icons.delete_outline_rounded),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

'''
s = s[:start] + new_pages + s[end:]

# Make each library open directly on its requested tab.
s = s.replace(
    "PremiumCatalogSheet(onShape: (i) {",
    "PremiumCatalogSheet(initialTab: initialTab, onShape: (i) {",
    1,
)

p.write_text(s, encoding='utf-8')
print('Premium editor catalog repair applied.')
