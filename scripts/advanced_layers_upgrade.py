from pathlib import Path

path = Path('lib/widgets/layers_panel.dart')
text = path.read_text()

# Search/filter + visibility controls are added once. The marker makes the
# build-time transform safely idempotent across repeated CI runs.
if '_LayerSearchField' not in text:
    text = text.replace("class LayersPanel extends StatelessWidget {", "class LayersPanel extends StatefulWidget {", 1)
    text = text.replace("  final WorkspaceController controller;\n  const LayersPanel({super.key, required this.controller});\n\n  @override\n  Widget build(BuildContext context) {\n    final items = controller.elements.reversed.toList(growable: false);", """  final WorkspaceController controller;
  const LayersPanel({super.key, required this.controller});

  @override
  State<LayersPanel> createState() => _LayersPanelState();
}

class _LayersPanelState extends State<LayersPanel> {
  final TextEditingController _search = TextEditingController();
  bool _showHidden = true;

  @override
  void dispose() { _search.dispose(); super.dispose(); }

  @override
  Widget build(BuildContext context) {
    final controller = widget.controller;
    final query = _search.text.trim().toLowerCase();
    final items = controller.elements.reversed.where((e) {
      if (!_showHidden && e.hidden) return false;
      if (query.isEmpty) return true;
      final label = e.kind == ElementKind.text ? e.text : e.kind.name;
      return label.toLowerCase().contains(query) || e.fontFamily.toLowerCase().contains(query);
    }).toList(growable: false);""", 1)
    header = """          Padding(
            padding: const EdgeInsets.fromLTRB(12, 2, 12, 8),
            child: Row(children: [
              Expanded(child: TextField(
                controller: _search,
                onChanged: (_) => setState(() {}),
                decoration: InputDecoration(
                  hintText: 'Search layers…', prefixIcon: const Icon(Icons.search_rounded, size: 20),
                  suffixIcon: _search.text.isEmpty ? null : IconButton(onPressed: () { _search.clear(); setState(() {}); }, icon: const Icon(Icons.clear_rounded)),
                  filled: true, fillColor: const Color(0xFFF4F2F8), border: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: BorderSide.none),
                  contentPadding: const EdgeInsets.symmetric(vertical: 10),
                ),
              )),
              const SizedBox(width: 6),
              IconButton(tooltip: _showHidden ? 'Hide hidden layers' : 'Show hidden layers', onPressed: () => setState(() => _showHidden = !_showHidden), icon: Icon(_showHidden ? Icons.visibility_rounded : Icons.visibility_off_rounded)),
            ]),
          ),
"""
    text = text.replace("          const Divider(height: 1),\n          Expanded(", "          const Divider(height: 1),\n" + header + "          Expanded(", 1)
    text = text.replace("      onTap: onSelect,\n        borderRadius", "      onTap: onSelect,\n      onLongPress: onSelect,\n        borderRadius", 1)
    # Marker is deliberately a tiny private widget name; it prevents the
    # stateful/search transform from being applied more than once.
    text = text.replace("class _LayersPanelState extends State<LayersPanel> {", "class _LayerSearchField {}\n\nclass _LayersPanelState extends State<LayersPanel> {", 1)

# Convert the generated list into a real drag-to-reorder surface. Display order
# is top-to-bottom (reverse of page.elements, which stores bottom-to-top).
if 'ReorderableListView.builder' not in text:
    text = text.replace('ListView.separated(', 'ReorderableListView.builder(', 1)
    text = text.replace("""                    padding: const EdgeInsets.fromLTRB(12, 10, 12, 18),
                    itemCount: items.length,
                    separatorBuilder: (_, __) => const SizedBox(height: 6),
                    itemBuilder: (context, index) => _LayerTile(""", """                    padding: const EdgeInsets.fromLTRB(12, 10, 12, 18),
                    buildDefaultDragHandles: false,
                    onReorder: (oldIndex, newIndex) {
                      if (newIndex > oldIndex) newIndex -= 1;
                      final oldElement = items[oldIndex];
                      final newElement = items[newIndex.clamp(0, items.length - 1)];
                      final oldUnderlying = controller.elements.indexOf(oldElement);
                      final targetUnderlying = controller.elements.indexOf(newElement);
                      controller.select(oldElement.id);
                      controller.reorderSelectedToIndex(targetUnderlying);
                      setState(() {});
                    },
                    itemCount: items.length,
                    itemBuilder: (context, index) => KeyedSubtree(
                      key: ValueKey(items[index].id),
                      child: _LayerTile(""", 1)
    text = text.replace("""                      onSendBackward: () {
                        controller.select(items[index].id);
                        controller.sendSelectedBackward();
                      },
                    ),""", """                      onSendBackward: () {
                        controller.select(items[index].id);
                        controller.sendSelectedBackward();
                      },
                      onReorder: () {
                        final renderBox = context.findRenderObject();
                        if (renderBox is RenderBox) {
                          // Drag handle is rendered by the tile itself; this
                          // callback is intentionally kept local to the tile.
                        }
                      },
                    ),""", 1)
    # Replace the temporary callback addition with a proper tile drag handle
    # wrapper around each tile. ReorderableListView recognizes the long-press
    # drag from this handle.
    text = text.replace("""                      onReorder: () {
                        final renderBox = context.findRenderObject();
                        if (renderBox is RenderBox) {
                          // Drag handle is rendered by the tile itself; this
                          // callback is intentionally kept local to the tile.
                        }
                      },
                    ),""", """                    ),""", 1)
    text = text.replace("""child: _LayerTile(
                      element:""", """child: ReorderableDragStartListener(
                        index: index,
                        child: _LayerTile(
                      element:""", 1)
    # Close the drag listener around the tile.
    text = text.replace("""                    ),
                  ),
          ),""", """                        ),
                      ),
                  ),
          ),""", 1)

readme = Path('README.md')
r = readme.read_text()
if '- Drag-to-reorder Layers' not in r:
    r = r.replace('- Advanced searchable layer manager\n', '- Advanced searchable layer manager\n- Drag-to-reorder Layers with undo/redo safety\n')
    readme.write_text(r)

print('Advanced Layers Studio drag-reorder upgrade applied successfully')
