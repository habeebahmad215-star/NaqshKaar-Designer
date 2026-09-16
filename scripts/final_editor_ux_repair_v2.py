from pathlib import Path
import re

# Deterministic final editor UX pass. It operates on the fully generated tree
# using structural anchors/regexes rather than formatting-sensitive snippets.

# Workspace ---------------------------------------------------------------
p = Path('lib/screens/workspace_screen.dart')
s = p.read_text(encoding='utf-8')

if "import '../widgets/layers_panel.dart';" not in s:
    s = s.replace("import '../widgets/design_canvas.dart';", "import '../widgets/design_canvas.dart';\nimport '../widgets/layers_panel.dart';", 1)

# Locate the AppBar action list only inside _buildAppBar.
app_start = s.find('  PreferredSizeWidget _buildAppBar()')
app_end = s.find('\n  Widget _buildCanvasArea()', app_start)
if app_start < 0 or app_end < 0:
    raise SystemExit('AppBar structural region not found')
app = s[app_start:app_end]
if "tooltip: 'Layers'" not in app:
    action_pos = app.find('actions: [')
    if action_pos < 0:
        raise SystemExit('AppBar actions list not found')
    insert_at = action_pos + len('actions: [')
    app = app[:insert_at] + "\n        IconButton(tooltip: 'Layers', onPressed: _layersSheet, icon: const Icon(Icons.layers_rounded))," + app[insert_at:]
    s = s[:app_start] + app + s[app_end:]

# Add the Layers sheet implementation if absent.
if 'Future<void> _layersSheet() async' not in s:
    marker = "  Widget _viewButton(IconData icon, String tooltip, VoidCallback onTap) {"
    method = '''  Future<void> _layersSheet() async {\n    await showModalBottomSheet<void>(\n      context: context,\n      isScrollControlled: true,\n      showDragHandle: true,\n      builder: (_) => SizedBox(\n        height: MediaQuery.sizeOf(context).height * .78,\n        child: LayersPanel(controller: controller),\n      ),\n    );\n  }\n\n'''
    if marker not in s:
        raise SystemExit('View-button anchor not found for Layers sheet')
    s = s.replace(marker, method + marker, 1)

# Selected toolbar: insert a highlighted Deselect action once.
if 'Widget _deselectTool()' not in s:
    marker = '  Widget _toggleTool(IconData icon, String label, bool active, VoidCallback onTap) {'
    method = '''  Widget _deselectTool() {\n    return Padding(\n      padding: const EdgeInsets.symmetric(horizontal: 3),\n      child: Material(\n        color: _primary,\n        borderRadius: BorderRadius.circular(12),\n        elevation: 1,\n        child: InkWell(\n          onTap: () => controller.select(null),\n          borderRadius: BorderRadius.circular(12),\n          child: const SizedBox(\n            width: 72,\n            child: Column(\n              mainAxisAlignment: MainAxisAlignment.center,\n              children: [\n                Icon(Icons.deselect_rounded, color: Colors.white, size: 21),\n                SizedBox(height: 3),\n                Text('Deselect', style: TextStyle(fontSize: 9, fontWeight: FontWeight.w900, color: Colors.white)),\n              ],\n            ),\n          ),\n        ),\n      ),\n    );\n  }\n\n'''
    if marker not in s:
        raise SystemExit('Selected toolbar toggle anchor not found')
    s = s.replace(marker, method + marker, 1)

if '_deselectTool(),' not in s:
    tools_pos = s.find('    final tools = <Widget>[', s.find('Widget _selectedToolbar'))
    if tools_pos < 0:
        raise SystemExit('Selected toolbar tools list not found')
    end = tools_pos + len('    final tools = <Widget>[')
    s = s[:end] + '\n      _deselectTool(),' + s[end:]

# Generic slider: update model during drag for live preview.
slider_pattern = re.compile(r'onChanged:\s*\(newValue\)\s*=>\s*setSheetState\(\(\)\s*=>\s*value\s*=\s*newValue\),')
if slider_pattern.search(s):
    s = slider_pattern.sub("onChanged: (newValue) { setSheetState(() => value = newValue); apply(newValue); },", s, count=1)

# Color and font selection are applied before closing their sheets.
s = s.replace("onTap: () => Navigator.pop(sheetContext, color),", "onTap: () { controller.updateSelected(colorValue: color.toARGB32()); Navigator.pop(sheetContext); },", 1)
s = s.replace("    if (color != null) controller.updateSelected(colorValue: color.toARGB32());", "    // Color is committed at swatch tap time for live preview.", 1)
s = s.replace("onTap: () => Navigator.pop(context, family),", "onTap: () { controller.setSelectedFont(family); Navigator.pop(context, family); },", 1)
s = s.replace("    if (family != null) controller.setSelectedFont(family);", "    // Font is committed at tile tap time for live preview.", 1)

# Effects and typography spacing live-preview callbacks.
repls = {
"_effectSlider('Stroke', strokeWidth, 0, 40, (v) => setSheetState(() => strokeWidth = v)),": "_effectSlider('Stroke', strokeWidth, 0, 40, (v) { setSheetState(() => strokeWidth = v); controller.setSelectedStroke(width: v, colorValue: element.strokeColorValue == 0 ? Colors.black.toARGB32() : element.strokeColorValue); }),",
"_effectSlider('Shadow Blur', shadowBlur, 0, 80, (v) => setSheetState(() => shadowBlur = v)),": "_effectSlider('Shadow Blur', shadowBlur, 0, 80, (v) { setSheetState(() => shadowBlur = v); controller.setSelectedShadow(blur: v, offsetX: shadowX, offsetY: shadowY, colorValue: element.shadowColorValue == 0 ? Colors.black54.toARGB32() : element.shadowColorValue); }),",
"_effectSlider('Shadow X', shadowX, -100, 100, (v) => setSheetState(() => shadowX = v)),": "_effectSlider('Shadow X', shadowX, -100, 100, (v) { setSheetState(() => shadowX = v); controller.setSelectedShadow(blur: shadowBlur, offsetX: v, offsetY: shadowY, colorValue: element.shadowColorValue == 0 ? Colors.black54.toARGB32() : element.shadowColorValue); }),",
"_effectSlider('Shadow Y', shadowY, -100, 100, (v) => setSheetState(() => shadowY = v)),": "_effectSlider('Shadow Y', shadowY, -100, 100, (v) { setSheetState(() => shadowY = v); controller.setSelectedShadow(blur: shadowBlur, offsetX: shadowX, offsetY: v, colorValue: element.shadowColorValue == 0 ? Colors.black54.toARGB32() : element.shadowColorValue); }),",
"_effectSlider('Letter Spacing', letterSpacing, -10, 20, (v) => setSheetState(() => letterSpacing = v)),": "_effectSlider('Letter Spacing', letterSpacing, -10, 20, (v) { setSheetState(() => letterSpacing = v); controller.setSelectedTypography(letterSpacing: v, lineHeight: lineHeight); }),",
"_effectSlider('Line Height', lineHeight, 0.7, 3, (v) => setSheetState(() => lineHeight = v)),": "_effectSlider('Line Height', lineHeight, 0.7, 3, (v) { setSheetState(() => lineHeight = v); controller.setSelectedTypography(letterSpacing: letterSpacing, lineHeight: v); }),",
}
for old, new in repls.items():
    s = s.replace(old, new, 1)

# Precise bottom label for catalog borders.
s = s.replace(
"""      case ElementKind.shape:\n        return 'Shape • ${element.width.round()} × ${element.height.round()}';""",
"""      case ElementKind.shape:\n        final kind = element.catalogType == 'border' ? 'Border' : 'Shape';\n        return '$kind • ${element.width.round()} × ${element.height.round()}';""",
1)
p.write_text(s, encoding='utf-8')

# Canvas ------------------------------------------------------------------
p = Path('lib/widgets/design_canvas.dart')
s = p.read_text(encoding='utf-8')
floating = re.compile(r"\n\s*Positioned\(\s*top:\s*8,\s*right:\s*8,\s*child:\s*Material\(\s*color:\s*Colors\.white,\s*elevation:\s*4,\s*borderRadius:\s*BorderRadius\.circular\(14\),\s*child:\s*IconButton\(\s*tooltip:\s*'Layers',\s*onPressed:\s*_layersSheet,\s*icon:\s*const Icon\(Icons\.layers_rounded,\s*color:\s*_purple\),\s*\),\s*\),\s*\),", re.DOTALL)
s, removed = floating.subn('', s, count=1)
if removed:
    s = re.sub(r"\n\s*Future<void> _layersSheet\(\) async \{.*?\n\s*\}\n", '\n', s, count=1, flags=re.DOTALL)
if 'radius: e.radius' not in s:
    s = s.replace('border: e.catalogType == \'border\',', "border: e.catalogType == 'border',\n              radius: e.radius,", 1)
p.write_text(s, encoding='utf-8')

# Catalog renderer -------------------------------------------------------
p = Path('lib/widgets/premium_catalogs.dart')
s = p.read_text(encoding='utf-8')
if 'final double radius;' not in s:
    s = s.replace('final int type; final Color fill; final Color stroke; final double strokeWidth; final bool border;', 'final int type; final Color fill; final Color stroke; final double strokeWidth; final bool border; final double radius;', 1)
if 'this.radius = 18' not in s:
    s = s.replace('required this.strokeWidth, this.border = false});', 'required this.strokeWidth, this.radius = 18, this.border = false});', 1)
# Make rectangle and rounded-box families radius-aware.
s = s.replace(
'case 0: canvas.drawRect(r,p); break; case 1: canvas.drawRRect(RRect.fromRectAndRadius(r,Radius.circular(_min(w,h)*.16)),p); break;',
'case 0: final rr = radius <= 0 ? null : RRect.fromRectAndRadius(r, Radius.circular(math.min(radius, _min(w, h) / 2))); if (rr == null) canvas.drawRect(r, p); else canvas.drawRRect(rr, p); break; case 1: canvas.drawRRect(RRect.fromRectAndRadius(r, Radius.circular(math.min(radius, _min(w, h) / 2))),p); break;',
1)
s = s.replace('Radius.circular(18+t%20.0)', 'Radius.circular(math.min(radius, math.min(q.width, q.height) / 2))', 1)
s = s.replace('oldDelegate.strokeWidth != strokeWidth || oldDelegate.border != border;', 'oldDelegate.strokeWidth != strokeWidth || oldDelegate.radius != radius || oldDelegate.border != border;', 1)
p.write_text(s, encoding='utf-8')

# Layers -----------------------------------------------------------------
p = Path('lib/widgets/layers_panel.dart')
s = p.read_text(encoding='utf-8')
if "import 'premium_catalogs.dart';" not in s:
    s = s.replace("import '../state/workspace_controller.dart';", "import '../state/workspace_controller.dart';\nimport 'premium_catalogs.dart';", 1)
old = """      case ElementKind.shape:\n        return 'Shape';"""
new = """      case ElementKind.shape:\n        if (element.catalogType == 'border') {\n          final index = element.shapeType.clamp(0, PremiumShapeCatalog.borderNames.length - 1).toInt();\n          return 'Border • ${PremiumShapeCatalog.borderNames[index]}';\n        }\n        if (element.catalogType == 'shape') {\n          final index = element.shapeType.clamp(0, PremiumShapeCatalog.shapeNames.length - 1).toInt();\n          return 'Shape • ${PremiumShapeCatalog.shapeNames[index]}';\n        }\n        return 'Shape';"""
if old in s:
    s = s.replace(old, new, 1)
old_sub = """      case ElementKind.shape:\n        return '${element.width.round()} × ${element.height.round()}';"""
new_sub = """      case ElementKind.shape:\n        final kind = element.catalogType == 'border' ? 'Border' : 'Shape';\n        return '$kind • ${element.width.round()} × ${element.height.round()}';"""
if old_sub in s:
    s = s.replace(old_sub, new_sub, 1)
p.write_text(s, encoding='utf-8')

# Hard invariants: fail here, before analyzer, if any requested contract is missing.
ws = Path('lib/screens/workspace_screen.dart').read_text(encoding='utf-8')
canvas = Path('lib/widgets/design_canvas.dart').read_text(encoding='utf-8')
cat = Path('lib/widgets/premium_catalogs.dart').read_text(encoding='utf-8')
layers = Path('lib/widgets/layers_panel.dart').read_text(encoding='utf-8')
for needle, text in [
    ("tooltip: 'Layers'", ws), ('Future<void> _layersSheet() async', ws), ('_deselectTool()', ws), ('radius: e.radius', canvas), ('final double radius;', cat), ('catalogType == \'border\'', layers), ('PremiumShapeCatalog.borderNames[index]', layers),
]:
    if needle not in text:
        raise SystemExit(f'Final UX invariant missing: {needle}')
print('Deterministic final editor UX repair applied successfully.')
