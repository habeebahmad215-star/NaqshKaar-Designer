from pathlib import Path

# Generate the complete layer manager in one deterministic pass. This avoids
# fragile incremental source substitutions and keeps repeated CI builds stable.
path = Path('lib/widgets/layers_panel.dart')
path.write_text(r'''import 'package:flutter/material.dart';

import '../models/design_models.dart';
import '../state/workspace_controller.dart';

/// Professional layer manager: search, visibility, locking, quick actions and
/// true drag-to-reorder. page.elements remains bottom-to-top; the UI shows
/// top-to-bottom so it matches what designers see on the canvas.
class LayersPanel extends StatefulWidget {
  final WorkspaceController controller;
  const LayersPanel({super.key, required this.controller});

  @override
  State<LayersPanel> createState() => _LayersPanelState();
}

class _LayersPanelState extends State<LayersPanel> {
  final TextEditingController _search = TextEditingController();
  bool _showHidden = true;

  @override
  void dispose() {
    _search.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final controller = widget.controller;
    final query = _search.text.trim().toLowerCase();
    final items = controller.elements.reversed.where((e) {
      if (!_showHidden && e.hidden) return false;
      if (query.isEmpty) return true;
      final label = e.kind == ElementKind.text ? e.text : e.kind.name;
      return label.toLowerCase().contains(query) || e.fontFamily.toLowerCase().contains(query);
    }).toList(growable: false);

    return SafeArea(
      child: Column(
        children: [
          const Padding(
            padding: EdgeInsets.fromLTRB(18, 4, 18, 8),
            child: Row(children: [
              Icon(Icons.layers_rounded, size: 22),
              SizedBox(width: 10),
              Expanded(child: Text('Layers', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w900))),
              Text('Top → Bottom', style: TextStyle(fontSize: 11, color: Colors.black45, fontWeight: FontWeight.w700)),
            ]),
          ),
          Padding(
            padding: const EdgeInsets.fromLTRB(12, 2, 12, 8),
            child: Row(children: [
              Expanded(child: TextField(
                controller: _search,
                onChanged: (_) => setState(() {}),
                decoration: InputDecoration(
                  hintText: 'Search layers…',
                  prefixIcon: const Icon(Icons.search_rounded, size: 20),
                  suffixIcon: _search.text.isEmpty ? null : IconButton(
                    onPressed: () { _search.clear(); setState(() {}); },
                    icon: const Icon(Icons.clear_rounded),
                  ),
                  filled: true,
                  fillColor: const Color(0xFFF4F2F8),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: BorderSide.none),
                  contentPadding: const EdgeInsets.symmetric(vertical: 10),
                ),
              )),
              const SizedBox(width: 6),
              IconButton(
                tooltip: _showHidden ? 'Hide hidden layers' : 'Show hidden layers',
                onPressed: () => setState(() => _showHidden = !_showHidden),
                icon: Icon(_showHidden ? Icons.visibility_rounded : Icons.visibility_off_rounded),
              ),
            ]),
          ),
          const Divider(height: 1),
          Expanded(
            child: items.isEmpty
                ? const Center(child: Column(mainAxisSize: MainAxisSize.min, children: [
                    Icon(Icons.layers_clear_outlined, size: 42, color: Colors.black26),
                    SizedBox(height: 10),
                    Text('No matching layers', style: TextStyle(fontWeight: FontWeight.w800)),
                    SizedBox(height: 4),
                    Text('Add text, shape or image to create a layer.', style: TextStyle(color: Colors.black45, fontSize: 12)),
                  ]))
                : ReorderableListView.builder(
                    padding: const EdgeInsets.fromLTRB(12, 10, 12, 18),
                    buildDefaultDragHandles: false,
                    itemCount: items.length,
                    onReorder: (oldIndex, newIndex) {
                      if (newIndex > oldIndex) newIndex -= 1;
                      if (newIndex < 0 || newIndex >= items.length) return;
                      final moving = items[oldIndex];
                      final target = items[newIndex];
                      final targetUnderlying = controller.elements.indexOf(target);
                      controller.select(moving.id);
                      controller.reorderSelectedToIndex(targetUnderlying);
                      setState(() {});
                    },
                    itemBuilder: (context, index) {
                      final element = items[index];
                      return KeyedSubtree(
                        key: ValueKey(element.id),
                        child: Padding(
                          padding: const EdgeInsets.only(bottom: 6),
                          child: _LayerTile(
                            element: element,
                            selected: element.id == controller.selectedId,
                            onSelect: () => controller.select(element.id),
                            onToggleVisibility: () { controller.select(element.id); controller.toggleSelectedHidden(); },
                            onToggleLock: () { controller.select(element.id); controller.toggleSelectedLock(); },
                            onDuplicate: () { controller.select(element.id); controller.duplicateSelected(); },
                            onDelete: () { controller.select(element.id); controller.deleteSelected(); },
                            onBringForward: () { controller.select(element.id); controller.bringSelectedForward(); },
                            onSendBackward: () { controller.select(element.id); controller.sendSelectedBackward(); },
                            dragHandle: ReorderableDragStartListener(
                              index: index,
                              child: const Padding(
                                padding: EdgeInsets.all(8),
                                child: Icon(Icons.drag_indicator_rounded, size: 22, color: Colors.black38),
                              ),
                            ),
                          ),
                        ),
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }
}

class _LayerTile extends StatelessWidget {
  final DesignElement element;
  final bool selected;
  final VoidCallback onSelect;
  final VoidCallback onToggleVisibility;
  final VoidCallback onToggleLock;
  final VoidCallback onDuplicate;
  final VoidCallback onDelete;
  final VoidCallback onBringForward;
  final VoidCallback onSendBackward;
  final Widget dragHandle;

  const _LayerTile({
    required this.element,
    required this.selected,
    required this.onSelect,
    required this.onToggleVisibility,
    required this.onToggleLock,
    required this.onDuplicate,
    required this.onDelete,
    required this.onBringForward,
    required this.onSendBackward,
    required this.dragHandle,
  });

  IconData get _icon {
    switch (element.kind) {
      case ElementKind.text: return Icons.text_fields_rounded;
      case ElementKind.shape: return Icons.crop_square_rounded;
      case ElementKind.image: return Icons.image_outlined;
    }
  }

  String get _title {
    switch (element.kind) {
      case ElementKind.text:
        final value = element.text.trim().replaceAll('\n', ' ');
        return value.isEmpty ? 'Urdu Text' : value.length > 28 ? '${value.substring(0, 28)}…' : value;
      case ElementKind.shape: return 'Shape';
      case ElementKind.image: return 'Image';
    }
  }

  String get _subtitle {
    switch (element.kind) {
      case ElementKind.text: return '${element.fontFamily} • ${element.fontSize.round()} px';
      case ElementKind.shape:
      case ElementKind.image: return '${element.width.round()} × ${element.height.round()}';
    }
  }

  @override
  Widget build(BuildContext context) {
    return Material(
      color: selected ? const Color(0xFFF1ECFF) : const Color(0xFFF8F8FA),
      borderRadius: BorderRadius.circular(16),
      child: InkWell(
        onTap: onSelect,
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
          child: Row(children: [
            Container(
              width: 42, height: 42,
              decoration: BoxDecoration(
                color: selected ? const Color(0xFF6D28D9) : Colors.white,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: selected ? const Color(0xFF6D28D9) : Colors.black12),
              ),
              child: Icon(_icon, color: selected ? Colors.white : Colors.black54, size: 21),
            ),
            const SizedBox(width: 9),
            Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text(_title, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w800)),
              const SizedBox(height: 3),
              Text(_subtitle, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 10, color: Colors.black45)),
            ])),
            IconButton(tooltip: element.hidden ? 'Show' : 'Hide', visualDensity: VisualDensity.compact, onPressed: onToggleVisibility, icon: Icon(element.hidden ? Icons.visibility_off_outlined : Icons.visibility_outlined, size: 19)),
            IconButton(tooltip: element.locked ? 'Unlock' : 'Lock', visualDensity: VisualDensity.compact, onPressed: onToggleLock, icon: Icon(element.locked ? Icons.lock_rounded : Icons.lock_open_rounded, size: 18)),
            PopupMenuButton<String>(
              tooltip: 'Layer actions', padding: EdgeInsets.zero,
              onSelected: (value) {
                switch (value) {
                  case 'forward': onBringForward(); break;
                  case 'backward': onSendBackward(); break;
                  case 'duplicate': onDuplicate(); break;
                  case 'delete': onDelete(); break;
                }
              },
              itemBuilder: (_) => const [
                PopupMenuItem(value: 'forward', child: Text('Bring forward')),
                PopupMenuItem(value: 'backward', child: Text('Send backward')),
                PopupMenuDivider(),
                PopupMenuItem(value: 'duplicate', child: Text('Duplicate')),
                PopupMenuItem(value: 'delete', child: Text('Delete')),
              ],
            ),
            dragHandle,
          ]),
        ),
      ),
    );
  }
}
''')

readme = Path('README.md')
r = readme.read_text()
if '- Drag-to-reorder Layers' not in r:
    r = r.replace('- Advanced searchable layer manager\n', '- Advanced searchable layer manager\n- Drag-to-reorder Layers with undo/redo safety\n')
    readme.write_text(r)

print('Advanced Layers Studio hardened successfully')
