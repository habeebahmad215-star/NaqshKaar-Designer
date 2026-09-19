from pathlib import Path

path = Path('lib/state/workspace_controller.dart')
text = path.read_text(encoding='utf-8')
old = "  void _checkpoint() { _history.add(ProjectModel.fromJson(project.toJson())); if (_history.length > 30) _history.removeAt(0); _future.clear(); }"
new = """  void _checkpoint() {
    if (_continuousCheckpointActive) return;
    _history.add(ProjectModel.fromJson(project.toJson()));
    if (_history.length > 30) _history.removeAt(0);
    _future.clear();
  }"""
if old in text:
    text = text.replace(old, new, 1)

# A continuous edit is a temporary transaction. Undo/redo must terminate that
# transaction so a later discrete action can create its own history checkpoint.
text = text.replace(
    "  void undo() { if (!canUndo) return; _future.add(ProjectModel.fromJson(project.toJson()));",
    "  void undo() { if (!canUndo) return; _continuousCheckpointActive = false; _future.add(ProjectModel.fromJson(project.toJson()));",
    1,
)
text = text.replace(
    "  void redo() { if (!canRedo) return; _history.add(ProjectModel.fromJson(project.toJson()));",
    "  void redo() { if (!canRedo) return; _continuousCheckpointActive = false; _history.add(ProjectModel.fromJson(project.toJson()));",
    1,
)

required = [
    'void _checkpoint() {',
    'if (_continuousCheckpointActive) return;',
    'void startContinuousEdit()',
    'void finishContinuousEdit()',
    '_continuousCheckpointActive = false; _future.add(',
    '_continuousCheckpointActive = false; _history.add(',
]
for needle in required:
    if needle not in text:
        raise SystemExit(f'Continuous checkpoint contract missing: {needle}')

for method_name in ['setSelectedRadius', 'setSelectedStroke', 'setSelectedShadow', 'setSelectedTypography', 'setSelectedFontSize']:
    start = text.find('void ' + method_name)
    if start < 0:
        raise SystemExit(f'Continuous-control method missing: {method_name}')
    end = text.find(r'\n  }', start)
    block = text[start:end]
    if '_checkpoint();' in block and 'if (!_continuousCheckpointActive) _checkpoint();' not in block:
        raise SystemExit(f'Unprotected continuous checkpoint in {method_name}')

workspace = Path('lib/screens/workspace_screen.dart').read_text(encoding='utf-8')
if 'onChangeEnd: (_) => controller.finishContinuousEdit()' not in workspace:
    raise SystemExit('Slider release checkpoint contract missing')
if 'controller.startContinuousEdit();' not in workspace:
    raise SystemExit('Slider continuous-start contract missing')

path.write_text(text, encoding='utf-8')
print('Continuous-edit transaction hardening verified: guarded checkpoint, single undo transaction, and undo/redo transaction reset.')
