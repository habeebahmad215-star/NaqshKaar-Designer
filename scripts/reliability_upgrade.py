from pathlib import Path

path = Path('lib/screens/workspace_screen.dart')
text = path.read_text()

if "import 'dart:async';" not in text:
    text = text.replace("import 'package:flutter/material.dart';", "import 'dart:async';\nimport 'package:flutter/material.dart';", 1)

fields = """  Timer? _autosaveTimer;\n  bool _autosaveInFlight = false;\n  bool _autosaveDirty = false;\n"""
if '_autosaveDirty' not in text:
    marker = "  final TransformationController _transform = TransformationController();\n"
    if marker not in text:
        raise SystemExit('Workspace field marker not found')
    text = text.replace(marker, marker + fields, 1)

old_init = """    controller = WorkspaceController(\n      initial: widget.initialProject,\n      newSize: widget.size,\n    );\n"""
new_init = old_init + "    controller.addListener(_scheduleAutosave);\n"
if '_scheduleAutosave' not in text:
    if old_init not in text:
        raise SystemExit('initState controller block not found')
    text = text.replace(old_init, new_init, 1)

old_dispose = """  @override\n  void dispose() {\n    _transform.dispose();\n    controller.dispose();\n    super.dispose();\n  }\n"""
new_dispose = """  @override\n  void dispose() {\n    _autosaveTimer?.cancel();\n    controller.removeListener(_scheduleAutosave);\n    _transform.dispose();\n    controller.dispose();\n    super.dispose();\n  }\n"""
if old_dispose in text:
    text = text.replace(old_dispose, new_dispose, 1)

methods = r'''  void _scheduleAutosave() {
    _autosaveDirty = true;
    _autosaveTimer?.cancel();
    _autosaveTimer = Timer(const Duration(milliseconds: 900), _autosave);
  }

  Future<void> _autosave() async {
    if (!_autosaveDirty || _autosaveInFlight) return;
    _autosaveDirty = false;
    _autosaveInFlight = true;
    try {
      await _repo.save(controller.project);
    } catch (_) {
      _autosaveDirty = true;
      // Manual Save remains available if the device is temporarily unable to write.
    } finally {
      _autosaveInFlight = false;
      if (_autosaveDirty && mounted) {
        _autosaveTimer?.cancel();
        _autosaveTimer = Timer(const Duration(milliseconds: 900), _autosave);
      }
    }
  }

'''
if 'Future<void> _autosave()' not in text:
    anchor = '  Future<void> _save() async {'
    if anchor not in text:
        raise SystemExit('_save method not found')
    text = text.replace(anchor, methods + anchor, 1)

text = text.replace("  Future<void> _save() async {\n    _autosaveTimer?.cancel();\n    try {", "  Future<void> _save() async {\n    _autosaveTimer?.cancel();\n    _autosaveDirty = false;\n    try {", 1)

path.write_text(text)
print('Crash-recovery autosave race fix applied successfully')
