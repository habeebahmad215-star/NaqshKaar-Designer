from pathlib import Path

W = Path('lib/screens/workspace_screen.dart')
C = Path('lib/state/workspace_controller.dart')

c = C.read_text(encoding='utf-8')
if 'void addTable(int rows, int cols)' not in c:
    anchor = '  DesignElement addImage(Uint8List bytes) {'
    if anchor not in c:
        raise SystemExit('controller anchor missing')
    insert = '''  void addTable(int rows, int cols) {
    if (rows < 1 || cols < 1) return;
    _checkpoint();
    final cellW = page.size.width / cols;
    final cellH = (page.size.height * .42 / rows).clamp(48.0, 140.0).toDouble();
    final totalH = cellH * rows;
    final top = (page.size.height - totalH) / 2;
    for (var r = 0; r < rows; r++) {
      for (var col = 0; col < cols; col++) {
        page.elements.add(DesignElement(
          id: _newId('cell'),
          kind: ElementKind.shape,
          x: col * cellW,
          y: top + r * cellH,
          width: cellW,
          height: cellH,
          colorValue: Colors.transparent.toARGB32(),
          strokeColorValue: const Color(0xFFCBD5E1).toARGB32(),
          strokeWidth: 2,
          radius: 0,
        ));
      }
    }
    selectedId = page.elements.isEmpty ? null : page.elements.last.id;
    _changed();
  }

'''
    c = c.replace(anchor, insert + anchor, 1)
    C.write_text(c, encoding='utf-8')

w = W.read_text(encoding='utf-8')
if "../widgets/studio_add_sheet.dart" not in w:
    w = w.replace(
        "import '../widgets/design_canvas.dart';",
        "import '../widgets/design_canvas.dart';\nimport '../widgets/layers_panel.dart';\nimport '../widgets/studio_add_sheet.dart';\nimport '../widgets/ai_studio_sheet.dart';",
        1,
    )
elif "../widgets/layers_panel.dart" not in w:
    w = w.replace(
        "import '../widgets/studio_add_sheet.dart';",
        "import '../widgets/layers_panel.dart';\nimport '../widgets/studio_add_sheet.dart';",
        1,
    )

needle = "_mainTool(Icons.tune_rounded, 'Design', _designSheet),"
if needle in w and "'Studio', _remainingToolsSheet" not in w:
    w = w.replace(
        needle,
        needle + "\n        _mainTool(Icons.apps_rounded, 'Studio', _remainingToolsSheet),",
        1,
    )

if 'Future<void> _remainingToolsSheet()' not in w:
    marker = """  Future<void> _aiStudioSheet() async {
    await showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      showDragHandle: true,
      backgroundColor: const Color(0xFFF7F7FA),
      builder: (_) => AiStudioSheet(
        onWriteResult: (text) => controller.addText(text: text, rtl: true),
        onImageResult: (bytes) => controller.addImage(bytes),
      ),
    );
  }

  Future<void> _addText() async {"""
    if marker not in w:
        raise SystemExit('workspace insertion marker missing')
    method = """  Future<void> _remainingToolsSheet() async {
    await showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      showDragHandle: true,
      backgroundColor: const Color(0xFFF7F7FA),
      builder: (sheetContext) => StudioAddSheet(
        onGallery: _pickImage,
        onText: _addText,
        onShape: controller.addShape,
        onTable: () async {
          final result = await _tableSizeDialog();
          if (result != null) controller.addTable(result.$1, result.$2);
        },
        onBackground: _backgroundSheet,
        onPages: _pagesSheet,
        onLayers: () async {
          Navigator.pop(sheetContext);
          await showModalBottomSheet<void>(
            context: context,
            isScrollControlled: true,
            showDragHandle: true,
            builder: (_) => SizedBox(
              height: MediaQuery.sizeOf(context).height * .72,
              child: LayersPanel(controller: controller),
            ),
          );
        },
        onEffects: _effectsSheet,
        onExport: () => _exportMenu('png'),
        onSpecialText: () async {
          controller.addText(text: 'بسم اللہ الرحمن الرحیم');
        },
        onImageStudio: controller.selected?.kind == ElementKind.image
            ? _imageStudioSheet
            : null,
        onAiStudio: _aiStudioSheet,
      ),
    );
  }

  Future<(int, int)?> _tableSizeDialog() async {
    var rows = 3;
    var cols = 3;
    return showDialog<(int, int)>(
      context: context,
      builder: (c) => StatefulBuilder(
        builder: (context, setState) => AlertDialog(
          title: const Text(
            'Table',
            style: TextStyle(fontWeight: FontWeight.w900),
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Row(
                children: [
                  const Expanded(child: Text('Rows')),
                  Expanded(
                    child: Slider(
                      min: 1,
                      max: 8,
                      divisions: 7,
                      value: rows.toDouble(),
                      onChanged: (v) => setState(() => rows = v.round()),
                    ),
                  ),
                  Text('$rows'),
                ],
              ),
              Row(
                children: [
                  const Expanded(child: Text('Columns')),
                  Expanded(
                    child: Slider(
                      min: 1,
                      max: 8,
                      divisions: 7,
                      value: cols.toDouble(),
                      onChanged: (v) => setState(() => cols = v.round()),
                    ),
                  ),
                  Text('$cols'),
                ],
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(c),
              child: const Text('Cancel'),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(c, (rows, cols)),
              child: const Text('Create'),
            ),
          ],
        ),
      ),
    );
  }

"""
    w = w.replace(marker, method + marker, 1)

W.write_text(w, encoding='utf-8')
print('Remaining Studio tool hub applied.')
