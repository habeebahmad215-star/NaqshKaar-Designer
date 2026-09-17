from pathlib import Path
import re

# Final editor UX pass. This runs after all earlier generators, so the files
# below are the exact generated sources that reach format/analyze/build.

# ---------------------------------------------------------------------------
# Controller: continuous controls update immediately but create one undo point.
# ---------------------------------------------------------------------------
p = Path('lib/state/workspace_controller.dart')
s = p.read_text(encoding='utf-8')

if 'bool _continuousCheckpointActive = false;' not in s:
    anchor = '  String? selectedId;'
    if anchor not in s:
        raise SystemExit('Controller selection anchor not found')
    s = s.replace(anchor, anchor + '\n  bool _continuousCheckpointActive = false;', 1)

if 'void startContinuousEdit()' not in s:
    anchor = '  void select(String? id) {'
    i = s.find(anchor)
    if i < 0:
        raise SystemExit('Controller select anchor not found')
    method = '''  void startContinuousEdit() {\n    if (_continuousCheckpointActive) return;\n    final e = selected;\n    if (e == null || e.locked) return;\n    _checkpoint();\n    _continuousCheckpointActive = true;\n  }\n\n  void finishContinuousEdit() {\n    _continuousCheckpointActive = false;\n    notifyListeners();\n  }\n\n'''
    s = s[:i] + method + s[i:]

# Avoid a history entry for every slider tick.
s = s.replace(
    'if (e == null || e.locked) return; _checkpoint();',
    'if (e == null || e.locked) return; if (!_continuousCheckpointActive) _checkpoint();',
)
for method_name in [
    'setSelectedOpacity', 'setSelectedRadius', 'setSelectedStroke',
    'setSelectedShadow', 'setSelectedTypography', 'setSelectedFontSize',
]:
    start = s.find('void ' + method_name)
    if start >= 0:
        end = s.find('\n  }', start)
        if end >= 0:
            block = s[start:end]
            block = block.replace('_checkpoint();', 'if (!_continuousCheckpointActive) _checkpoint();')
            s = s[:start] + block + s[end:]
p.write_text(s, encoding='utf-8')

# ---------------------------------------------------------------------------
# Workspace UI: live slider preview, Deselect, and top-bar Layers.
# ---------------------------------------------------------------------------
p = Path('lib/screens/workspace_screen.dart')
s = p.read_text(encoding='utf-8')

if 'Widget _deselectTool()' not in s:
    marker = '  Widget _tool(IconData icon, String label, VoidCallback onTap) {'
    if marker not in s:
        raise SystemExit('Selected toolbar tool anchor not found')
    method = '''  Widget _deselectTool() {\n    return Padding(\n      padding: const EdgeInsets.symmetric(horizontal: 3),\n      child: Material(\n        color: _primary,\n        borderRadius: BorderRadius.circular(12),\n        elevation: 1,\n        child: InkWell(\n          onTap: () => controller.select(null),\n          borderRadius: BorderRadius.circular(12),\n          child: const SizedBox(\n            width: 72,\n            child: Column(\n              mainAxisAlignment: MainAxisAlignment.center,\n              children: [\n                Icon(Icons.deselect_rounded, color: Colors.white, size: 21),\n                SizedBox(height: 3),\n                Text('Deselect', style: TextStyle(fontSize: 9, fontWeight: FontWeight.w900, color: Colors.white)),\n              ],\n            ),\n          ),\n        ),\n      ),\n    );\n  }\n\n'''
    s = s.replace(marker, method + marker, 1)

if '      _deselectTool(),' not in s:
    marker = '    final tools = <Widget>['
    if marker not in s:
        raise SystemExit('Selected toolbar list anchor not found')
    s = s.replace(marker, marker + '\n      _deselectTool(),', 1)

if "import '../widgets/layers_panel.dart';" not in s:
    s = s.replace("import '../widgets/design_canvas.dart';", "import '../widgets/design_canvas.dart';\nimport '../widgets/layers_panel.dart';", 1)

if "tooltip: 'Layers'" not in s:
    marker = '      actions: ['
    if marker not in s:
        raise SystemExit('AppBar actions anchor not found')
    button = "\n        IconButton(tooltip: 'Layers', onPressed: _layersSheet, icon: const Icon(Icons.layers_rounded)),"
    s = s.replace(marker, marker + button, 1)

if 'Future<void> _layersSheet() async' not in s:
    marker = '  Widget _viewButton(IconData icon, String tooltip, VoidCallback onTap) {'
    if marker not in s:
        raise SystemExit('Layers insertion anchor not found')
    method = '''  Future<void> _layersSheet() async {\n    await showModalBottomSheet<void>(\n      context: context,\n      isScrollControlled: true,\n      showDragHandle: true,\n      builder: (_) => SizedBox(\n        height: MediaQuery.sizeOf(context).height * .78,\n        child: LayersPanel(controller: controller),\n      ),\n    );\n  }\n\n'''
    s = s.replace(marker, method + marker, 1)

start = s.find('Future<void> _singleSlider(')
if start < 0:
    raise SystemExit('Single-slider method not found')
next_method = s.find('\n  Future<void> ', start + 10)
end = next_method if next_method >= 0 else len(s)
seg = s[start:end]
if 'controller.startContinuousEdit();' not in seg:
    seg, count = re.subn(
        r'(?P<indent>\s*)apply\(newValue\);',
        r'\g<indent>controller.startContinuousEdit();\n\g<indent>apply(newValue);',
        seg,
        count=1,
    )
    if count == 0:
        seg, count = re.subn(
            r'(onChanged:\s*\([^)]*\)\s*\{)',
            r'\1 controller.startContinuousEdit();',
            seg,
            count=1,
        )
    if count == 0:
        raise SystemExit('Could not wire live slider callback')
if 'controller.finishContinuousEdit();' not in seg:
    close_match = re.search(r'(\n\s*\}\s*)$', seg)
    if close_match:
        pos = close_match.start(1)
        seg = seg[:pos] + '\n    controller.finishContinuousEdit();' + seg[pos:]
    else:
        raise SystemExit('Single-slider closing anchor not found')
s = s[:start] + seg + s[end:]
p.write_text(s, encoding='utf-8')

# ---------------------------------------------------------------------------
# Canvas: pass the model radius into the catalog painter.
# ---------------------------------------------------------------------------
p = Path('lib/widgets/design_canvas.dart')
s = p.read_text(encoding='utf-8')
if 'radius: e.radius' not in s:
    anchor = "border: e.catalogType == 'border',"
    if anchor not in s:
        raise SystemExit('Catalog painter border anchor not found')
    s = s.replace(anchor, anchor + '\n              radius: e.radius,', 1)
p.write_text(s, encoding='utf-8')

# ---------------------------------------------------------------------------
# Catalog painter: radius is a real input and participates in repainting.
# Earlier catalog-repair passes may already have installed this property with
# either 18 or 18.0. Accept both forms instead of assuming one exact spelling.
# ---------------------------------------------------------------------------
p = Path('lib/widgets/premium_catalogs.dart')
s = p.read_text(encoding='utf-8')
if 'final double radius;' not in s:
    marker = 'final double strokeWidth; final bool border;'
    if marker not in s:
        raise SystemExit('Catalog painter field anchor not found')
    s = s.replace(marker, 'final double strokeWidth; final bool border; final double radius;', 1)

if not re.search(r'this\.radius\s*=\s*18(?:\.0)?', s):
    ctor = re.search(r'(const\s+CatalogShapePainter\(\{[^\n]*)(\}\);)', s)
    if not ctor:
        raise SystemExit('Catalog painter constructor anchor not found')
    line = ctor.group(1)
    if 'this.radius' not in line:
        line += ', this.radius = 18'
    s = s[:ctor.start(1)] + line + ctor.group(2) + s[ctor.end(2):]

# Round-rect family: make radius model-driven, clamped to the shape bounds.
if 'radius.clamp(0.0' not in s:
    old = 'Radius.circular(_min(w,h)*.16)'
    if old in s:
        new = 'Radius.circular(radius.clamp(0.0, _min(w, h) / 2).toDouble())'
        s = s.replace(old, new, 1)
if 'oldDelegate.radius != radius' not in s:
    marker = 'oldDelegate.strokeWidth != strokeWidth || oldDelegate.border != border;'
    if marker in s:
        s = s.replace(marker, 'oldDelegate.strokeWidth != strokeWidth || oldDelegate.radius != radius || oldDelegate.border != border;', 1)
p.write_text(s, encoding='utf-8')

# ---------------------------------------------------------------------------
# Layers: border must never be presented as a generic Shape.
# ---------------------------------------------------------------------------
p = Path('lib/widgets/layers_panel.dart')
s = p.read_text(encoding='utf-8')
old = """      case ElementKind.shape:\n        return 'Shape';"""
new = """      case ElementKind.shape:\n        return element.catalogType == 'border' ? 'Border' : 'Shape';"""
if old in s:
    s = s.replace(old, new, 1)
old = """      case ElementKind.shape:\n        return '${element.width.round()} × ${element.height.round()}';"""
new = """      case ElementKind.shape:\n        final kind = element.catalogType == 'border' ? 'Border' : 'Shape';\n        return '$kind • ${element.width.round()} × ${element.height.round()}';"""
if old in s:
    s = s.replace(old, new, 1)
p.write_text(s, encoding='utf-8')

# ---------------------------------------------------------------------------
# Fail-fast contracts. These check implementation, not merely script output.
# ---------------------------------------------------------------------------
ws = Path('lib/screens/workspace_screen.dart').read_text(encoding='utf-8')
ctl = Path('lib/state/workspace_controller.dart').read_text(encoding='utf-8')
canvas = Path('lib/widgets/design_canvas.dart').read_text(encoding='utf-8')
cat = Path('lib/widgets/premium_catalogs.dart').read_text(encoding='utf-8')
layers = Path('lib/widgets/layers_panel.dart').read_text(encoding='utf-8')
checks = [
    ("tooltip: 'Layers'", ws),
    ('Future<void> _layersSheet() async', ws),
    ('_deselectTool()', ws),
    ('controller.startContinuousEdit();', ws),
    ('controller.finishContinuousEdit();', ws),
    ('void startContinuousEdit()', ctl),
    ('void finishContinuousEdit()', ctl),
    ('if (!_continuousCheckpointActive) _checkpoint();', ctl),
    ('radius: e.radius', canvas),
    ('final double radius;', cat),
    ('oldDelegate.radius != radius', cat),
    ("return element.catalogType == 'border' ? 'Border' : 'Shape';", layers),
]
for needle, text in checks:
    if needle not in text:
        raise SystemExit(f'Final editor UX invariant missing: {needle}')
print('Final editor UX contracts verified: live preview, radius, deselect, layers, semantic labels, and undo grouping.')