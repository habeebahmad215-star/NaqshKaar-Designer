from pathlib import Path
import re

# Canvas interaction's broad move-method replacement can consume methods that
# sit between moveSelectedBy and the resize doc comment. Re-install the layer
# reorder API after all controller transforms so the generated build always
# has the API used by Layers Studio.
controller_path = Path('lib/state/workspace_controller.dart')
controller = controller_path.read_text()

if 'void reorderSelectedToIndex(int targetIndex)' not in controller:
    marker = '  /// Resizes in the element\'s local coordinate system.'
    method = '''  /// Moves the selected layer to a concrete stack index. The index uses the
  /// same bottom-to-top ordering as page.elements and is undoable as one action.
  void reorderSelectedToIndex(int targetIndex) {
    final e = selected;
    if (e == null || e.locked) return;
    final oldIndex = elements.indexOf(e);
    if (oldIndex < 0 || elements.length < 2) return;
    final clamped = targetIndex.clamp(0, elements.length - 1).toInt();
    if (oldIndex == clamped) return;
    _checkpoint();
    elements.removeAt(oldIndex);
    final destination = clamped > oldIndex ? clamped - 1 : clamped;
    elements.insert(destination.clamp(0, elements.length).toInt(), e);
    _changed();
  }

'''
    if marker not in controller:
        raise SystemExit('controller resize marker not found')
    controller = controller.replace(marker, method + marker, 1)

# Layer reordering now uses the modern ReorderableListView callback. Unlike
# onReorder, onReorderItem already adjusts the destination after removal.
layers_path = Path('lib/widgets/layers_panel.dart')
layers = layers_path.read_text()
pattern = r"\s*onReorder: \(oldIndex, newIndex\) \{.*?\n\s*\},\n\s*itemBuilder:"
replacement = '''
                    onReorderItem: (oldIndex, newIndex) {
                      if (oldIndex < 0 || oldIndex >= items.length || newIndex < 0 || newIndex >= items.length) return;
                      final moving = items[oldIndex];
                      final target = items[newIndex];
                      final targetUnderlying = controller.elements.indexOf(target);
                      controller.select(moving.id);
                      controller.reorderSelectedToIndex(targetUnderlying);
                      setState(() {});
                    },
                    itemBuilder:'''
layers, count = re.subn(pattern, replacement, layers, count=1, flags=re.S)
if count != 1:
    raise SystemExit('Layers reorder callback not found')

layers_path.write_text(layers)
controller_path.write_text(controller)
print('Layers Studio build integration fixed: reorder API restored and modern reorder callback enabled.')
