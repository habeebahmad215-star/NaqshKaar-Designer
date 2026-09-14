import 'package:flutter/material.dart';

import '../models/design_models.dart';
import '../state/workspace_controller.dart';

/// Reusable professional layer manager for the editor workspace.
/// Elements are displayed top-most first so the visual stacking order is
/// immediately understandable to a designer.
class LayersPanel extends StatelessWidget {
  final WorkspaceController controller;
  const LayersPanel({super.key, required this.controller});

  @override
  Widget build(BuildContext context) {
    final items = controller.elements.reversed.toList(growable: false);
    return SafeArea(
      child: Column(
        children: [
          const Padding(
            padding: EdgeInsets.fromLTRB(18, 4, 18, 10),
            child: Row(
              children: [
                Icon(Icons.layers_rounded, size: 22),
                SizedBox(width: 10),
                Expanded(
                  child: Text('Layers', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w900)),
                ),
                Text('Top → Bottom', style: TextStyle(fontSize: 11, color: Colors.black45, fontWeight: FontWeight.w700)),
              ],
            ),
          ),
          const Divider(height: 1),
          Expanded(
            child: items.isEmpty
                ? const Center(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.layers_clear_outlined, size: 42, color: Colors.black26),
                        SizedBox(height: 10),
                        Text('No elements yet', style: TextStyle(fontWeight: FontWeight.w800)),
                        SizedBox(height: 4),
                        Text('Add text, shape or image to create a layer.', style: TextStyle(color: Colors.black45, fontSize: 12)),
                      ],
                    ),
                  )
                : ListView.separated(
                    padding: const EdgeInsets.fromLTRB(12, 10, 12, 18),
                    itemCount: items.length,
                    separatorBuilder: (_, __) => const SizedBox(height: 6),
                    itemBuilder: (context, index) => _LayerTile(
                      element: items[index],
                      selected: items[index].id == controller.selectedId,
                      onSelect: () => controller.select(items[index].id),
                      onToggleVisibility: () {
                        controller.select(items[index].id);
                        controller.toggleSelectedHidden();
                      },
                      onToggleLock: () {
                        controller.select(items[index].id);
                        controller.toggleSelectedLock();
                      },
                      onDuplicate: () {
                        controller.select(items[index].id);
                        controller.duplicateSelected();
                      },
                      onDelete: () {
                        controller.select(items[index].id);
                        controller.deleteSelected();
                      },
                      onBringForward: () {
                        controller.select(items[index].id);
                        controller.bringSelectedForward();
                      },
                      onSendBackward: () {
                        controller.select(items[index].id);
                        controller.sendSelectedBackward();
                      },
                    ),
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
  });

  IconData get _icon {
    switch (element.kind) {
      case ElementKind.text:
        return Icons.text_fields_rounded;
      case ElementKind.shape:
        return Icons.crop_square_rounded;
      case ElementKind.image:
        return Icons.image_outlined;
    }
  }

  String get _title {
    switch (element.kind) {
      case ElementKind.text:
        final value = element.text.trim().replaceAll('\n', ' ');
        return value.isEmpty ? 'Urdu Text' : value.length > 28 ? '${value.substring(0, 28)}…' : value;
      case ElementKind.shape:
        return 'Shape';
      case ElementKind.image:
        return 'Image';
    }
  }

  String get _subtitle {
    switch (element.kind) {
      case ElementKind.text:
        return '${element.fontFamily} • ${element.fontSize.round()} px';
      case ElementKind.shape:
        return '${element.width.round()} × ${element.height.round()}';
      case ElementKind.image:
        return '${element.width.round()} × ${element.height.round()}';
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
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 9),
          child: Row(
            children: [
              Container(
                width: 42,
                height: 42,
                decoration: BoxDecoration(
                  color: selected ? const Color(0xFF6D28D9) : Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: selected ? const Color(0xFF6D28D9) : Colors.black12),
                ),
                child: Icon(_icon, color: selected ? Colors.white : Colors.black54, size: 21),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(_title, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w800)),
                    const SizedBox(height: 3),
                    Text(_subtitle, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 10, color: Colors.black45)),
                  ],
                ),
              ),
              IconButton(tooltip: element.hidden ? 'Show' : 'Hide', visualDensity: VisualDensity.compact, onPressed: onToggleVisibility, icon: Icon(element.hidden ? Icons.visibility_off_outlined : Icons.visibility_outlined, size: 19)),
              IconButton(tooltip: element.locked ? 'Unlock' : 'Lock', visualDensity: VisualDensity.compact, onPressed: onToggleLock, icon: Icon(element.locked ? Icons.lock_rounded : Icons.lock_open_rounded, size: 18)),
              PopupMenuButton<String>(
                tooltip: 'Layer actions',
                padding: EdgeInsets.zero,
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
            ],
          ),
        ),
      ),
    );
  }
}
