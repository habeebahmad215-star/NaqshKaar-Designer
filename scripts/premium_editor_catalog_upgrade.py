from pathlib import Path

# Final build-stage pass: repair the mobile editor UX and add large ready-made libraries.

# Model metadata for catalog elements.
p = Path('lib/models/design_models.dart'); s = p.read_text(encoding='utf-8')
if 'String catalogType;' not in s:
    s = s.replace('  double radius;\n', "  double radius;\n  String catalogType;\n  int shapeType;\n", 1)
    s = s.replace('    this.radius = 18,\n', "    this.radius = 18,\n    this.catalogType = '',\n    this.shapeType = 0,\n", 1)
    s = s.replace("'imageBytes': imageBytes == null ? null : base64Encode(imageBytes!), 'radius': radius,", "'imageBytes': imageBytes == null ? null : base64Encode(imageBytes!), 'radius': radius, 'catalogType': catalogType, 'shapeType': shapeType,")
    s = s.replace("imageBytes: bytes, radius: (json['radius'] as num?)?.toDouble() ?? 18,", "imageBytes: bytes, radius: (json['radius'] as num?)?.toDouble() ?? 18,\n      catalogType: json['catalogType']?.toString() ?? '', shapeType: (json['shapeType'] as num?)?.toInt() ?? 0,")
    p.write_text(s, encoding='utf-8')

# Controller actions for ready-made shapes and borders.
p = Path('lib/state/workspace_controller.dart'); s = p.read_text(encoding='utf-8')
if 'void addCatalogShape(int shapeType)' not in s:
    anchor = '  DesignElement addImage(Uint8List bytes) {'
    methods = '''  void addCatalogShape(int shapeType) {
    _checkpoint();
    final w = page.size.width * .42, h = page.size.height * .30;
    final e = DesignElement(id: _newId('shape'), kind: ElementKind.shape, x: (page.size.width-w)/2, y: (page.size.height-h)/2, width: w, height: h, colorValue: const Color(0xFF7C3AED).toARGB32(), strokeColorValue: const Color(0xFF6D28D9).toARGB32(), strokeWidth: 3, catalogType: 'shape', shapeType: shapeType);
    page.elements.add(e); selectedId = e.id; _changed();
  }

  void addBorder(int borderType) {
    _checkpoint();
    final e = DesignElement(id: _newId('border'), kind: ElementKind.shape, x: 12, y: 12, width: page.size.width-24, height: page.size.height-24, colorValue: Colors.transparent.toARGB32(), strokeColorValue: const Color(0xFFD4AF37).toARGB32(), strokeWidth: 4, radius: 18, catalogType: 'border', shapeType: borderType);
    page.elements.add(e); selectedId = e.id; _changed();
  }

'''
    if anchor not in s: raise SystemExit('controller anchor missing')
    s = s.replace(anchor, methods + anchor, 1)
    p.write_text(s, encoding='utf-8')

# Canvas rendering for catalog shapes/borders; do not let FittedBox silently shrink text.
p = Path('lib/widgets/design_canvas.dart'); s = p.read_text(encoding='utf-8')
if "premium_catalogs.dart" not in s:
    s = s.replace("import 'layers_panel.dart';", "import 'layers_panel.dart';\nimport 'premium_catalogs.dart';", 1)
old = """      case ElementKind.shape:
        child = DecoratedBox(decoration: _decoration(e, isShape: true));
        break;"""
new = """      case ElementKind.shape:
        if (e.catalogType == 'shape' || e.catalogType == 'border') {
          child = CustomPaint(painter: CatalogShapePainter(type: e.shapeType, fill: e.color, stroke: e.strokeColor.a > 0 ? e.strokeColor : _purple, strokeWidth: e.strokeWidth > 0 ? e.strokeWidth : 3, border: e.catalogType == 'border'));
        } else {
          child = DecoratedBox(decoration: _decoration(e, isShape: true));
        }
        break;"""
if old not in s: raise SystemExit('canvas shape block missing')
s = s.replace(old, new, 1)
old2 = """          child: FittedBox(
            fit: BoxFit.scaleDown,
            alignment: Alignment.center,
            child: SizedBox(
              width: e.width,
              child: Text("""
new2 = """          child: SizedBox(
            width: e.width,
            height: e.height,
            child: Text("""
if old2 in s:
    s = s.replace(old2, new2, 1)
    s = s.replace("""                ),
              ),
            ),
          ),
        );""", """                ),
              ),
          ),
        );""", 1)
p.write_text(s, encoding='utf-8')

# Workspace UX: 5-100 font size, robust page sheet, and catalog launchers.
p = Path('lib/screens/workspace_screen.dart'); s = p.read_text(encoding='utf-8')
if "premium_catalog_sheet.dart" not in s:
    s = s.replace("import '../widgets/layers_panel.dart';", "import '../widgets/layers_panel.dart';\nimport '../widgets/premium_catalog_sheet.dart';", 1)
s = s.replace("_mainTool(Icons.crop_square_rounded, 'Shape', controller.addShape),", "_mainTool(Icons.category_rounded, 'Shapes', _shapeLibrary),", 1)
s = s.replace("Future<void> _fontSize(DesignElement element) => _singleSlider('Font Size', element.fontSize, 8, 300", "Future<void> _fontSize(DesignElement element) => _singleSlider('Font Size', element.fontSize, 5, 100", 1)
if 'Future<void> _shapeLibrary()' not in s:
    marker = '  Future<void> _addText() async {'
    methods = '''  Future<void> _openPremiumLibrary({int initialTab = 0}) async {
    await showModalBottomSheet<void>(context: context, isScrollControlled: true, showDragHandle: true, builder: (_) => PremiumCatalogSheet(onShape: (i) { Navigator.pop(context); controller.addCatalogShape(i); }, onBorder: (i) { Navigator.pop(context); controller.addBorder(i); }, onSpecialText: (i) { Navigator.pop(context); controller.addText(text: PremiumSpecialText.value(i)); }));
  }
  Future<void> _shapeLibrary() async => _openPremiumLibrary(initialTab: 0);
  Future<void> _borderLibrary() async => _openPremiumLibrary(initialTab: 1);
  Future<void> _specialTextLibrary() async => _openPremiumLibrary(initialTab: 2);

'''
    s = s.replace(marker, methods + marker, 1)
# Route the existing Studio hub to the new libraries.
s = s.replace('onShape: controller.addShape,', 'onShape: _shapeLibrary,', 1)
s = s.replace('onShape: _shapeLibrary,\n        onTable:', 'onShape: _shapeLibrary,\n        onBorder: _borderLibrary,\n        onTable:', 1)
s = s.replace("onSpecialText: () async {\n          controller.addText(text: 'بسم اللہ الرحمن الرحیم');\n        },", 'onSpecialText: _specialTextLibrary,', 1)
# Replace the page sheet so Add Page stays fixed and clickable while pages scroll.
start = s.find('  Future<void> _pagesSheet() async {')
end = s.find('  Future<void> _designSheet() async {', start)
if start != -1 and end != -1:
    new = '''  Future<void> _pagesSheet() async {
    await showModalBottomSheet<void>(context: context, isScrollControlled: true, showDragHandle: true,
      builder: (sheetContext) => SafeArea(child: SizedBox(height: MediaQuery.sizeOf(context).height * .82,
        child: Column(children: [
          const _SheetHeader('Pages', 'Multi-page project workspace'),
          Expanded(child: ListView.builder(itemCount: controller.project.pages.length, itemBuilder: (context, index) {
            final selected = index == controller.currentPageIndex;
            return ListTile(leading: CircleAvatar(backgroundColor: selected ? _primary : Colors.black12, child: Text('${index+1}', style: TextStyle(color: selected ? Colors.white : Colors.black87))), title: Text(controller.project.pages[index].title), subtitle: Text('${controller.project.pages[index].size.width.round()} × ${controller.project.pages[index].size.height.round()}'), trailing: selected ? const Icon(Icons.check_circle_rounded, color: _primary) : null, onTap: () { controller.switchPage(index); Navigator.pop(sheetContext); });
          })),
          const Divider(height: 1),
          Padding(padding: const EdgeInsets.fromLTRB(16,8,16,10), child: Row(children: [
            Expanded(child: FilledButton.icon(onPressed: () { controller.addPage(); Navigator.pop(sheetContext); }, icon: const Icon(Icons.add_rounded), label: const Text('Add Page'))),
            const SizedBox(width: 8), Expanded(child: OutlinedButton.icon(onPressed: controller.project.pages.length > 1 ? () { controller.duplicatePage(); Navigator.pop(sheetContext); } : null, icon: const Icon(Icons.copy_all_outlined), label: const Text('Duplicate'))),
            const SizedBox(width: 4), IconButton(tooltip: 'Delete page', onPressed: controller.project.pages.length > 1 ? () { controller.deletePage(); Navigator.pop(sheetContext); } : null, icon: const Icon(Icons.delete_outline_rounded)),
          ])),
        ])));
  }

'''
    s = s[:start] + new + s[end:]
p.write_text(s, encoding='utf-8')

# Studio hub: add explicit Borders 100+ tile and upgrade existing labels.
p = Path('lib/widgets/studio_add_sheet.dart'); s = p.read_text(encoding='utf-8')
if 'final VoidCallback onBorder;' not in s:
    s = s.replace('  final VoidCallback onShape;\n', '  final VoidCallback onShape;\n  final VoidCallback onBorder;\n', 1)
    s = s.replace('required this.onShape, required this.onTable', 'required this.onShape, required this.onBorder, required this.onTable', 1)
    s = s.replace("_ToolItem(Icons.category_rounded, 'Shapes', 'Design primitives', onShape,", "_ToolItem(Icons.category_rounded, 'Shapes 100+', 'Ready-made shapes', onShape,", 1)
    s = s.replace("_ToolItem(Icons.auto_awesome_rounded, 'Special Text', 'Calligraphy starter', onSpecialText,", "_ToolItem(Icons.auto_awesome_rounded, 'Special Text 100+', 'Calligraphy library', onSpecialText,", 1)
    anchor = "_ToolItem(Icons.grid_4x4_rounded, 'Table', 'Rows & columns', onTable,"
    s = s.replace(anchor, "_ToolItem(Icons.crop_square_rounded, 'Borders 100+', 'Frames & ornaments', onBorder, const Color(0xFFB7791F)),\n      " + anchor, 1)
p.write_text(s, encoding='utf-8')
print('Premium editor catalog upgrade applied.')
