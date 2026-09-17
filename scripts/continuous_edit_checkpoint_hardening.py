from pathlib import Path

path = Path('lib/state/workspace_controller.dart')
text = path.read_text(encoding='utf-8')
old = "  void _checkpoint() { _history.add(ProjectModel.fromJson(project.toJson())); if (_history.length > 30) _history.removeAt(0); _future.clear(); }"
new = "  void _checkpoint() {\n    if (_continuousCheckpointActive) return;\n    _history.add(ProjectModel.fromJson(project.toJson()));\n    if (_history.length > 30) _history.removeAt(0);\n    _future.clear();\n  }"
if old in text:
    text = text.replace(old, new, 1)
path.write_text(text, encoding='utf-8')
if new not in text:
    raise SystemExit('Continuous checkpoint hardening contract missing')
print('Continuous-edit checkpoint hardening verified.')
