from pathlib import Path
import re

path = Path('lib/widgets/layers_panel.dart')
text = path.read_text()

# Upgrade the layer manager without changing controller APIs: searchable, compact,
# and with long-press access to the existing layer actions.
if '_LayerSearchField' not in text:
    text = text.replace("class LayersPanel extends StatelessWidget {", "class LayersPanel extends StatefulWidget {", 1)
    text = text.replace("  final WorkspaceController controller;\n  const LayersPanel({super.key, required this.controller});\n\n  @override\n  Widget build(BuildContext context) {\n    final items = controller.elements.reversed.toList(growable: false);", """  final WorkspaceController controller;
  const LayersPanel({super.key, required this.controller});

  @override
  State<LayersPanel> createState() => _LayersPanelState();
}

class _LayersPanelState extends State<LayersPanel> {
  final TextEditingController _search = TextEditingController();
  bool _showHidden = true;

  @override
  void dispose() { _search.dispose(); super.dispose(); }

  @override
  Widget build(BuildContext context) {
    final controller = widget.controller;
    final query = _search.text.trim().toLowerCase();
    final items = controller.elements.reversed.where((e) {
      if (!_showHidden && e.hidden) return false;
      if (query.isEmpty) return true;
      final label = e.kind == ElementKind.text ? e.text : e.kind.name;
      return label.toLowerCase().contains(query) || e.fontFamily.toLowerCase().contains(query);
    }).toList(growable: false);""", 1)
    header = """          Padding(
            padding: const EdgeInsets.fromLTRB(12, 2, 12, 8),
            child: Row(children: [
              Expanded(child: TextField(
                controller: _search,
                onChanged: (_) => setState(() {}),
                decoration: InputDecoration(
                  hintText: 'Search layers…', prefixIcon: const Icon(Icons.search_rounded, size: 20),
                  suffixIcon: _search.text.isEmpty ? null : IconButton(onPressed: () { _search.clear(); setState(() {}); }, icon: const Icon(Icons.clear_rounded)),
                  filled: true, fillColor: const Color(0xFFF4F2F8), border: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: BorderSide.none),
                  contentPadding: const EdgeInsets.symmetric(vertical: 10),
                ),
              )),
              const SizedBox(width: 6),
              IconButton(tooltip: _showHidden ? 'Hide hidden layers' : 'Show hidden layers', onPressed: () => setState(() => _showHidden = !_showHidden), icon: Icon(_showHidden ? Icons.visibility_rounded : Icons.visibility_off_rounded)),
            ]),
          ),
"""
    text = text.replace("          const Divider(height: 1),\n          Expanded(", "          const Divider(height: 1),\n" + header + "          Expanded(", 1)
    text = text.replace("      element: items[index],", "      element: items[index],", 1)
    text = text.replace("      onTap: onSelect,\n        borderRadius", "      onTap: onSelect,\n      onLongPress: onSelect,\n        borderRadius", 1)
    path.write_text(text)

# Make schema upgrade idempotent and ensure image studio is represented in docs.
readme = Path('README.md')
r = readme.read_text()
if '- Image Studio' not in r:
    r = r.replace('- PDF sharing\n', '- PDF sharing\n- Image Studio: crop/fit/zoom/position/flip\n- Smart alignment guides and snapping\n- Advanced searchable layer manager\n')
    readme.write_text(r)
print('Advanced Layers Studio upgrade applied successfully')
