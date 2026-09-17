from pathlib import Path
import re

# Final runtime UX pass. This runs after every earlier editor generator, so the
# generated Dart tree is the single source of truth that reaches analyzer/build.

# ---------------------------------------------------------------------------
# Controller: continuous slider edits get one undo checkpoint while every tick
# still updates the live canvas.
# ---------------------------------------------------------------------------
p = Path('lib/state/workspace_controller.dart')
s = p.read_text(encoding='utf-8')

# updateSelected is shared by opacity/color and must not create one history item
# per slider tick when a continuous edit is active.
s = s.replace(
    'void updateSelected({double? x, double? y, double? width, double? height, double? rotation, double? opacity, int? colorValue}) { final e = selected; if (e == null || e.locked) return; _checkpoint();',
    'void updateSelected({double? x, double? y, double? width, double? height, double? rotation, double? opacity, int? colorValue}) { final e = selected; if (e == null || e.locked) return; if (!_continuousCheckpointActive) _checkpoint();',
    1,
)
for old in [
    '_checkpoint(); e.radius = value.clamp(0, 240); _changed();',
    '_checkpoint(); e.strokeWidth = width.clamp(0, 40); e.strokeColorValue = colorValue; _changed();',
    '_checkpoint(); e.shadowBlur = blur.clamp(0, 80); e.shadowOffsetX = offsetX.clamp(-100, 100); e.shadowOffsetY = offsetY.clamp(-100, 100); e.shadowColorValue = colorValue; _changed();',
    '_checkpoint(); if (letterSpacing != null) e.letterSpacing = letterSpacing.clamp(-10, 20); if (lineHeight != null) e.lineHeight = lineHeight.clamp(.7, 3); _changed();',
    '_checkpoint(); e.fontSize = value.clamp(5, 300); _changed();',
]:
    if old in s:
        s = s.replace(old, old.replace('_checkpoint();', 'if (!_continuousCheckpointActive) _checkpoint();'), 1)
    else:
        # These methods are optional in some generated variants; do not fail on
        # an absent nonessential setter.
        pass
p.write_text(s, encoding='utf-8')

# ---------------------------------------------------------------------------
# Workspace: slider drag starts one continuous edit and commits every tick.
# ---------------------------------------------------------------------------
p = Path('lib/screens/workspace_screen.dart')
s = p.read_text(encoding='utf-8')

start = s.find('  Future<void> _singleSlider(')
end = s.find('\n  Future<void> _colorSheet()', start)
if start < 0 or end < 0:
    raise SystemExit('Single-slider structural region not found')
seg = s[start:end]
seg = seg.replace(
    'onChanged: (newValue) { setSheetState(() => value = newValue); apply(newValue); },',
    'onChanged: (newValue) { controller.startContinuousEdit(); setSheetState(() => value = newValue); apply(newValue); },',
    1,
)
if 'controller.finishContinuousEdit();' not in seg:
    seg = re.sub(r'\n  }\s*$', '\n    controller.finishContinuousEdit();\n  }', seg)
s = s[:start] + seg + s[end:]

# The selected toolbar must always offer an explicit deselect action.
if 'Widget _deselectTool()' not in s:
    marker = '  Widget _toggleTool(IconData icon, String label, bool active, VoidCallback onTap) {'
    method = '''  Widget _deselectTool() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 3),
      child: Material(
        color: _primary,
        borderRadius: BorderRadius.circular(12),
        elevation: 1,
        child: InkWell(
          onTap: () => controller.select(null),
          borderRadius: BorderRadius.circular(12),
          child: const SizedBox(
            width: 72,
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.deselect_rounded, color: Colors.white, size: 21),
                SizedBox(height: 3),
                Text('Deselect', style: TextStyle(fontSize: 9, fontWeight: FontWeight.w900, color: Colors.white)),
              ],
            ),
          ),
        ),
      ),
    );
  }

'''
    if marker not in s:
        raise SystemExit('Selected toolbar anchor not found')
    s = s.replace(marker, method + marker, 1)
if '_deselectTool(),' not in s:
    pos = s.find('    final tools = <Widget>[', s.find('Widget _selectedToolbar'))
    if pos < 0:
        raise SystemExit('Selected toolbar list not found')
    pos += len('    final tools = <Widget>[')
    s = s[:pos] + '\n      _deselectTool(),' + s[pos:]

# Layers belongs in the AppBar, not over the canvas.
if "import '../widgets/layers_panel.dart';" not in s:
    s = s.replace("import '../widgets/design_canvas.dart';", "import '../widgets/design_canvas.dart';\nimport '../widgets/layers_panel.dart';", 1)
app_start = s.find('  PreferredSizeWidget _buildAppBar()')
app_end = s.find('\n  Widget _buildCanvasArea()', app_start)
if app_start < 0 or app_end < 0:
    raise SystemExit('AppBar region not found')
app = s[app_start:app_end]
if "tooltip: 'Layers'" not in app:
    anchor = 'actions: ['
    i = app.find(anchor)
    if i < 0:
        raise SystemExit('AppBar actions anchor not found')
    i += len(anchor)
    app = app[:i] + "\n        IconButton(tooltip: 'Layers', onPressed: _layersSheet, icon: const Icon(Icons.layers_rounded))," + app[i:]
    s = s[:app_start] + app + s[app_end:]
if 'Future<void> _layersSheet() async' not in s:
    marker = "  Widget _viewButton(IconData icon, String tooltip, VoidCallback onTap) {"
    method = '''  Future<void> _layersSheet() async {
    await showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      showDragHandle: true,
      builder: (_) => SizedBox(
        height: MediaQuery.sizeOf(context).height * .78,
        child: LayersPanel(controller: controller),
      ),
    );
  }

'''
    if marker not in s:
        raise SystemExit('View-button anchor not found')
    s = s.replace(marker, method + marker, 1)
p.write_text(s, encoding='utf-8')

# ---------------------------------------------------------------------------
# Canvas/catalog: radius is a real painter input, including rounded frames.
# ---------------------------------------------------------------------------
p = Path('lib/widgets/design_canvas.dart')
s = p.read_text(encoding='utf-8')
if 'radius: e.radius' not in s:
    s = s.replace("border: e.catalogType == 'border',", "border: e.catalogType == 'border',\n              radius: e.radius,", 1)
p.write_text(s, encoding='utf-8')

p = Path('lib/widgets/premium_catalogs.dart')
s = p.read_text(encoding='utf-8')
if 'final double radius;' not in s:
    s = s.replace(
        'final int type; final Color fill; final Color stroke; final double strokeWidth; final bool border;',
        'final int type; final Color fill; final Color stroke; final double strokeWidth; final bool border; final double radius;',
        1,
    )
if 'this.radius = 18' not in s:
    s = s.replace(
        'required this.strokeWidth, this.border = false});',
        'required this.strokeWidth, this.radius = 18.0, this.border = false});',
        1,
    )
s = s.replace(
    'case 0: canvas.drawRect(r,p); break; case 1: canvas.drawRRect(RRect.fromRectAndRadius(r,Radius.circular(_min(w,h)*.16)),p); break;',
    'case 0: final double cr = math.min(radius.clamp(0.0, _min(w, h) / 2).toDouble(), _min(w, h) / 2); if (cr <= 0) { canvas.drawRect(r, p); } else { canvas.drawRRect(RRect.fromRectAndRadius(r, Radius.circular(cr)), p); } break; case 1: canvas.drawRRect(RRect.fromRectAndRadius(r, Radius.circular(math.min(radius.clamp(0.0, _min(w, h) / 2).toDouble(), _min(w, h) / 2))),p); break;',
    1,
)
s = s.replace('Radius.circular(18+t%20.0)', 'Radius.circular(math.min(radius.clamp(0.0, math.min(q.width, q.height) / 2).toDouble(), math.min(q.width, q.height) / 2))', 1)
if 'oldDelegate.radius != radius' not in s:
    s = s.replace('oldDelegate.strokeWidth != strokeWidth || oldDelegate.border != border;', 'oldDelegate.strokeWidth != strokeWidth || oldDelegate.radius != radius || oldDelegate.border != border;', 1)
p.write_text(s, encoding='utf-8')

# ---------------------------------------------------------------------------
# Layers: semantic names must distinguish catalog borders from shapes.
# ---------------------------------------------------------------------------
p = Path('lib/widgets/layers_panel.dart')
s = p.read_text(encoding='utf-8')
if "import 'premium_catalogs.dart';" not in s:
    s = s.replace("import '../state/workspace_controller.dart';", "import '../state/workspace_controller.dart';\nimport 'premium_catalogs.dart';", 1)
if "PremiumShapeCatalog.borderNames[index]" not in s:
    old = """      case ElementKind.shape:
        return 'Shape';"""
    new = """      case ElementKind.shape:
        if (element.catalogType == 'border') {
          final int index = element.shapeType.clamp(0, PremiumShapeCatalog.borderNames.length - 1).toInt();
          return 'Border • ${PremiumShapeCatalog.borderNames[index]}';
        }
        if (element.catalogType == 'shape') {
          final int index = element.shapeType.clamp(0, PremiumShapeCatalog.shapeNames.length - 1).toInt();
          return 'Shape • ${PremiumShapeCatalog.shapeNames[index]}';
        }
        return 'Shape';"""
    if old in s:
        s = s.replace(old, new, 1)
    else:
        raise SystemExit('Layer shape-title anchor not found')
s = s.replace(
    "      case ElementKind.shape:\n        return '${element.width.round()} × ${element.height.round()}';",
    "      case ElementKind.shape:\n        final String kind = element.catalogType == 'border' ? 'Border' : 'Shape';\n        return '$kind • ${element.width.round()} × ${element.height.round()}';",
    1,
)
p.write_text(s, encoding='utf-8')

# ---------------------------------------------------------------------------
# Fail-fast verification before dart format/analyze/build.
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
    ('if (!_continuousCheckpointActive) _checkpoint();', ctl),
    ('radius: e.radius', canvas),
    ('final double radius;', cat),
    ('oldDelegate.radius != radius', cat),
    ("PremiumShapeCatalog.borderNames[index]", layers),
    ("element.catalogType == 'border'", layers),
]
for needle, text in checks:
    if needle not in text:
        raise SystemExit(f'Final live-preview UX invariant missing: {needle}')
print('Final live-preview, radius, selection, layers, and semantic-label contracts verified.')
