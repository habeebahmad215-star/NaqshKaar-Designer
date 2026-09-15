from pathlib import Path

PATH = Path('lib/screens/workspace_screen.dart')
text = PATH.read_text(encoding='utf-8')


def replace_method(source: str, signature: str, replacement: str) -> str:
    start = source.index(signature)
    brace = source.index('{', start)
    depth = 0
    for i in range(brace, len(source)):
        if source[i] == '{':
            depth += 1
        elif source[i] == '}':
            depth -= 1
            if depth == 0:
                return source[:start] + replacement.rstrip() + source[i + 1:]
    raise SystemExit(f'Could not close method: {signature}')


def remove_method(source: str, signature: str) -> str:
    start = source.find(signature)
    if start < 0:
        return source
    brace = source.find('{', start)
    depth = 0
    for i in range(brace, len(source)):
        if source[i] == '{':
            depth += 1
        elif source[i] == '}':
            depth -= 1
            if depth == 0:
                return source[:start] + source[i + 1:]
    raise SystemExit(f'Could not remove method: {signature}')


old_top = "_topAction(Icons.redo_rounded, 'Redo', controller.canRedo ? controller.redo : null),"
new_top = old_top + "\n                  _topAction(Icons.ios_share_rounded, 'Export', () => _exportMenu('png')),"
if old_top not in text:
    raise SystemExit('Expected premium top toolbar anchor not found')
text = text.replace(old_top, new_top, 1)

old_second = """    final second = <Widget>[\n      _bottomTool(Icons.remove_circle_outline_rounded, 'Deselect', () => controller.select(null), active: true),\n      if (isText) _bottomTool(Icons.font_download_outlined, 'Font', _fontSheet),\n      _bottomTool(Icons.palette_outlined, 'Color', _colorSheet),\n      _bottomTool(Icons.auto_awesome_rounded, 'Effects', _effectsSheet),\n      if (isText) _bottomTool(Icons.translate_rounded, 'RTL / LTR', _directionSheet),\n      _bottomTool(Icons.more_horiz_rounded, 'More', _moreSheet),\n    ];"""
new_second = """    final second = <Widget>[\n      _bottomTool(Icons.remove_circle_outline_rounded, 'Deselect', () => controller.select(null), active: true),\n      if (isText) _bottomTool(Icons.edit_rounded, 'Edit', _editText),\n      if (isText) _bottomTool(Icons.font_download_outlined, 'Font', _fontSheet),\n      if (isText) _bottomTool(Icons.format_size_rounded, 'Size', () => _fontSize(element)),\n      _bottomTool(Icons.palette_outlined, 'Color', _colorSheet),\n      _bottomTool(Icons.auto_awesome_rounded, 'Effects', _effectsSheet),\n      if (isText) _bottomTool(Icons.format_line_spacing_rounded, 'Spacing', _spacingSheet),\n      if (isText) _bottomTool(Icons.format_align_center_rounded, 'Align', _alignSheet),\n      if (element.kind == ElementKind.shape) _bottomTool(Icons.rounded_corner, 'Corners', _radius),\n      _bottomTool(Icons.open_with_rounded, 'Arrange', _arrangeSheet),\n      if (element.kind == ElementKind.image) _bottomTool(Icons.tune_rounded, 'Image Studio', _imageStudioSheet),\n      if (isText) _bottomTool(Icons.text_format_rounded, 'Typography', _typographyStudioSheet),\n      _bottomTool(Icons.more_horiz_rounded, 'More', _moreSheet),\n    ];"""
if old_second not in text:
    raise SystemExit('Expected selected secondary toolbar anchor not found')
text = text.replace(old_second, new_second, 1)

text = replace_method(text, '  Widget _toolStrip(List<Widget> tools)', r'''  Widget _toolStrip(List<Widget> tools) {
    return SizedBox(
      height: 68,
      child: ListView(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 4),
        children: tools,
      ),
    );
  }''')

for signature in [
    '  Widget _headerButton(',
    '  Widget _viewButton(',
    '  Widget _mainTool(',
    '  Widget _quickAction(',
    '  String _elementLabel(',
    '  Widget _tool(',
    '  Widget _toggleTool(',
]:
    text = remove_method(text, signature)

PATH.write_text(text, encoding='utf-8')
print('Removed obsolete toolbar helpers and wired the demo-style feature actions.')
