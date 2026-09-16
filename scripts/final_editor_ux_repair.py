from pathlib import Path
import re

# Final editor UX pass. This runs after all existing generators so the runtime
# tree, not an intermediate source snapshot, owns these interaction contracts.

# 1) Workspace toolbar: move Layers to the top app bar and add a clearly
# highlighted Deselect action to the selected-object bottom bar.
p = Path('lib/screens/workspace_screen.dart')
s = p.read_text(encoding='utf-8')

# Add the layers panel import if needed.
if "layers_panel.dart" not in s:
    s = s.replace("import '../widgets/design_canvas.dart';", "import '../widgets/design_canvas.dart';\nimport '../widgets/layers_panel.dart';", 1)

# Add a compact, always-available Layers action to the top app bar.
anchor = """        IconButton(\n          tooltip: 'Undo',"""
if "tooltip: 'Layers'" not in s:
    replacement = """        IconButton(\n          tooltip: 'Layers',\n          onPressed: _layersSheet,\n          icon: const Icon(Icons.layers_rounded),\n        ),\n        IconButton(\n          tooltip: 'Undo',"""
    if anchor not in s:
        raise SystemExit('AppBar undo anchor not found')
    s = s.replace(anchor, replacement, 1)

# Ensure the selected toolbar starts with a prominent deselect control.
if "_deselectTool()" not in s:
    marker = "    final tools = <Widget>[\n"
    insert = """    final tools = <Widget>[\n      _deselectTool(),\n"""
    if marker not in s:
        raise SystemExit('Selected toolbar tools anchor not found')
    s = s.replace(marker, insert, 1)

# Add the highlighted deselect widget before _toggleTool.
if "Widget _deselectTool()" not in s:
    marker = "  Widget _toggleTool(IconData icon, String label, bool active, VoidCallback onTap) {"
    method = '''  Widget _deselectTool() {\n    return Padding(\n      padding: const EdgeInsets.symmetric(horizontal: 3),\n      child: Material(\n        color: _primary,\n        borderRadius: BorderRadius.circular(12),\n        elevation: 1,\n        child: InkWell(\n          onTap: () => controller.select(null),\n          borderRadius: BorderRadius.circular(12),\n          child: const SizedBox(\n            width: 72,\n            child: Column(\n              mainAxisAlignment: MainAxisAlignment.center,\n              children: [\n                Icon(Icons.deselect_rounded, color: Colors.white, size: 21),\n                SizedBox(height: 3),\n                Text('Deselect', style: TextStyle(fontSize: 9, fontWeight: FontWeight.w900, color: Colors.white)),\n              ],\n            ),\n          ),\n        ),\n      ),\n    );\n  }\n\n'''
    if marker not in s:
        raise SystemExit('Toggle tool anchor not found')
    s = s.replace(marker, method + marker, 1)

# Make every slider control update the controller as the finger moves.
old = """onChanged: (newValue) => setSheetState(() => value = newValue),"""
new = """onChanged: (newValue) {\n                      setSheetState(() => value = newValue);\n                      apply(newValue);\n                    },"""
if old in s:
    s = s.replace(old, new, 1)

# Effects: update both stroke and shadow live while the sheet is open.
s = s.replace(
    "_effectSlider('Stroke', strokeWidth, 0, 40, (v) => setSheetState(() => strokeWidth = v)),",
    "_effectSlider('Stroke', strokeWidth, 0, 40, (v) { setSheetState(() => strokeWidth = v); controller.setSelectedStroke(width: v, colorValue: element.strokeColorValue == 0 ? Colors.black.toARGB32() : element.strokeColorValue); }),",
    1,
)
s = s.replace(
    "_effectSlider('Shadow Blur', shadowBlur, 0, 80, (v) => setSheetState(() => shadowBlur = v)),",
    "_effectSlider('Shadow Blur', shadowBlur, 0, 80, (v) { setSheetState(() => shadowBlur = v); controller.setSelectedShadow(blur: v, offsetX: shadowX, offsetY: shadowY, colorValue: element.shadowColorValue == 0 ? Colors.black54.toARGB32() : element.shadowColorValue); }),",
    1,
)
s = s.replace(
    "_effectSlider('Shadow X', shadowX, -100, 100, (v) => setSheetState(() => shadowX = v)),",
    "_effectSlider('Shadow X', shadowX, -100, 100, (v) { setSheetState(() => shadowX = v); controller.setSelectedShadow(blur: shadowBlur, offsetX: v, offsetY: shadowY, colorValue: element.shadowColorValue == 0 ? Colors.black54.toARGB32() : element.shadowColorValue); }),",
    1,
)
s = s.replace(
    "_effectSlider('Shadow Y', shadowY, -100, 100, (v) => setSheetState(() => shadowY = v)),",
    "_effectSlider('Shadow Y', shadowY, -100, 100, (v) { setSheetState(() => shadowY = v); controller.setSelectedShadow(blur: shadowBlur, offsetX: shadowX, offsetY: v, colorValue: element.shadowColorValue == 0 ? Colors.black54.toARGB32() : element.shadowColorValue); }),",
    1,
)

# Typography spacing: live-update both values.
s = s.replace(
    "_effectSlider('Letter Spacing', letterSpacing, -10, 20, (v) => setSheetState(() => letterSpacing = v)),",
    "_effectSlider('Letter Spacing', letterSpacing, -10, 20, (v) { setSheetState(() => letterSpacing = v); controller.setSelectedTypography(letterSpacing: v, lineHeight: lineHeight); }),",
    1,
)
s = s.replace(
    "_effectSlider('Line Height', lineHeight, 0.7, 3, (v) => setSheetState(() => lineHeight = v)),",
    "_effectSlider('Line Height', lineHeight, 0.7, 3, (v) { setSheetState(() => lineHeight = v); controller.setSelectedTypography(letterSpacing: letterSpacing, lineHeight: v); }),",
    1,
)

# Color swatches should commit immediately on tap, rather than waiting for
# the bottom sheet to close.
old_color = """onTap: () => Navigator.pop(sheetContext, color),"""
new_color = """onTap: () {\n                    controller.updateSelected(colorValue: color.toARGB32());\n                    Navigator.pop(sheetContext);\n                  },"""
if old_color in s:
    s = s.replace(old_color, new_color, 1)
# Prevent a second delayed color application from being necessary.
s = s.replace(
    """    if (color != null) controller.updateSelected(colorValue: color.toARGB32());\n""",
    """    // Color is applied at swatch tap time for immediate canvas feedback.\n""",
    1,
)

# Font choices also apply at tap time.
s = s.replace(
    "onTap: () => Navigator.pop(context, family),",
    "onTap: () { controller.setSelectedFont(family); Navigator.pop(context, family); },",
    1,
)
s = s.replace(
    """    if (family != null) controller.setSelectedFont(family);\n""",
    """    // Font is applied at tile tap time for immediate canvas feedback.\n""",
    1,
)

# Catalog shape/border label is kept precise in the bottom toolbar.
old_label = """      case ElementKind.shape:\n        return 'Shape • ${element.width.round()} × ${element.height.round()}';"""
new_label = """      case ElementKind.shape:\n        if (element.catalogType == 'border') {\n          return 'Border • ${element.width.round()} × ${element.height.round()}';\n        }\n        if (element.catalogType == 'shape') {\n          return 'Shape • ${element.width.round()} × ${element.height.round()}';\n        }\n        return 'Shape • ${element.width.round()} × ${element.height.round()}';"""
if old_label in s:
    s = s.replace(old_label, new_label, 1)

p.write_text(s, encoding='utf-8')

# 2) Canvas: the small floating Layers button no longer competes with the
# design surface; the top app bar owns it.
p = Path('lib/widgets/design_canvas.dart')
s = p.read_text(encoding='utf-8')
floating = re.compile(r"\n        Positioned\(\n          top: 8,\n          right: 8,\n          child: Material\(\n            color: Colors\.white,\n            elevation: 4,\n            borderRadius: BorderRadius\.circular\(14\),\n            child: IconButton\(\n              tooltip: 'Layers',\n              onPressed: _layersSheet,\n              icon: const Icon\(Icons\.layers_rounded, color: _purple\),\n            \),\n          \),\n        \),", re.DOTALL)
s, removed = floating.subn('', s, count=1)
if removed:
    # Remove the now-unused private sheet method too.
    s = re.sub(r"\n  Future<void> _layersSheet\(\) async \{.*?\n  \}\n", '\n', s, count=1, flags=re.DOTALL)

# Pass the persisted radius into catalog painters. Both catalog and ordinary
# shapes therefore share the same model property.
s = s.replace(
    "strokeWidth: strokeWidth,\n              border: e.catalogType == 'border',",
    "strokeWidth: strokeWidth,\n              border: e.catalogType == 'border',\n              radius: e.radius,",
    1,
)
p.write_text(s, encoding='utf-8')

# 3) Catalog renderer: make radius a real visual property for rectangle and
# rounded-box families, and let border variants honor it where applicable.
p = Path('lib/widgets/premium_catalogs.dart')
s = p.read_text(encoding='utf-8')
if 'final double radius;' not in s:
    s = s.replace(
        'final int type; final Color fill; final Color stroke; final double strokeWidth; final bool border;',
        'final int type; final Color fill; final Color stroke; final double strokeWidth; final bool border; final double radius;',
        1,
    )
    s = s.replace(
        'required this.strokeWidth, this.border = false});',
        'required this.strokeWidth, this.radius = 18, this.border = false});',
        1,
    )

# Rectangle + rounded rectangle must respond to the live radius value.
s = s.replace(
    "case 0: canvas.drawRect(r,p); break; case 1: canvas.drawRRect(RRect.fromRectAndRadius(r,Radius.circular(_min(w,h)*.16)),p); break;",
    "case 0: final rr = radius <= 0 ? null : RRect.fromRectAndRadius(r, Radius.circular(math.min(radius, _min(w, h) / 2))); if (rr == null) canvas.drawRect(r, p); else canvas.drawRRect(rr, p); break; case 1: canvas.drawRRect(RRect.fromRectAndRadius(r, Radius.circular(math.min(radius, _min(w, h) / 2))),p); break;",
    1,
)
# Extend the border helper signature and rounded cases.
s = s.replace('void _drawBorder(Canvas c,Rect r,Paint p,int t){', 'void _drawBorder(Canvas c,Rect r,Paint p,int t){', 1)
# The border renderer already has rounded variants; replace hard-coded radius
# with the selected model radius while retaining safe caps.
s = s.replace('Radius.circular(18+t%20.0)', 'Radius.circular(math.min(radius, math.min(q.width, q.height) / 2))', 1)
# Add radius to repaint equality.
s = s.replace(
    'oldDelegate.strokeWidth != strokeWidth || oldDelegate.border != border;',
    'oldDelegate.strokeWidth != strokeWidth || oldDelegate.radius != radius || oldDelegate.border != border;',
    1,
)
p.write_text(s, encoding='utf-8')

# 4) Layers panel: explicitly distinguish border catalog items from shapes.
p = Path('lib/widgets/layers_panel.dart')
s = p.read_text(encoding='utf-8')
if "premium_catalogs.dart" not in s:
    s = s.replace("import '../state/workspace_controller.dart';", "import '../state/workspace_controller.dart';\nimport 'premium_catalogs.dart';", 1)
old = """      case ElementKind.shape:\n        return 'Shape';"""
new = """      case ElementKind.shape:\n        if (element.catalogType == 'border') {\n          final index = element.shapeType.clamp(0, PremiumShapeCatalog.borderNames.length - 1);\n          return 'Border • ${PremiumShapeCatalog.borderNames[index]}';\n        }\n        if (element.catalogType == 'shape') {\n          final index = element.shapeType.clamp(0, PremiumShapeCatalog.shapeNames.length - 1);\n          return 'Shape • ${PremiumShapeCatalog.shapeNames[index]}';\n        }\n        return 'Shape';"""
if old not in s:
    raise SystemExit('Layer shape title anchor not found')
s = s.replace(old, new, 1)
old_sub = """      case ElementKind.shape:\n        return '${element.width.round()} × ${element.height.round()}';"""
new_sub = """      case ElementKind.shape:\n        final kind = element.catalogType == 'border' ? 'Border' : 'Shape';\n        return '$kind • ${element.width.round()} × ${element.height.round()}';"""
if old_sub in s:
    s = s.replace(old_sub, new_sub, 1)
p.write_text(s, encoding='utf-8')

# Final structural invariants: fail early rather than allowing a misleading
# green build if one of the expected UX contracts was not generated.
checks = {
    Path('lib/screens/workspace_screen.dart'): ["tooltip: 'Layers'", "_deselectTool()", "apply(newValue)", "Border •"],
    Path('lib/widgets/design_canvas.dart'): ['radius: e.radius'],
    Path('lib/widgets/premium_catalogs.dart'): ['final double radius;', 'oldDelegate.radius != radius'],
    Path('lib/widgets/layers_panel.dart'): ['catalogType == ' + "'border'", 'PremiumShapeCatalog.borderNames'],
}
for path, needles in checks.items():
    text = path.read_text(encoding='utf-8')
    for needle in needles:
        if needle not in text:
            raise SystemExit(f'UX invariant missing in {path}: {needle}')

print('Final editor UX repair applied: live controls, radius rendering, top Layers, Deselect, and precise layer labels.')
