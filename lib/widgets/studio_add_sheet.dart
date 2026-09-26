import 'package:flutter/material.dart';

class StudioAddSheet extends StatelessWidget {
  final VoidCallback onGallery;
  final VoidCallback onText;
  final VoidCallback onShape;
  final VoidCallback onTable;
  final VoidCallback onBackground;
  final VoidCallback onPages;
  final VoidCallback onLayers;
  final VoidCallback onEffects;
  final VoidCallback onExport;
  final VoidCallback onSpecialText;
  final VoidCallback? onImageStudio;
  final VoidCallback? onAiStudio;

  const StudioAddSheet({super.key, required this.onGallery, required this.onText, required this.onShape, required this.onTable, required this.onBackground, required this.onPages, required this.onLayers, required this.onEffects, required this.onExport, required this.onSpecialText, this.onImageStudio, this.onAiStudio});

  @override
  Widget build(BuildContext context) {
    final items = <_ToolItem>[
      _ToolItem(Icons.photo_library_rounded, 'Gallery Pic', 'Import image', onGallery, const Color(0xFF2563EB)),
      _ToolItem(Icons.text_fields_rounded, 'Add Text', 'Urdu composer', onText, const Color(0xFFF97316)),
      _ToolItem(Icons.auto_awesome_rounded, 'Special Text', 'Calligraphy starter', onSpecialText, const Color(0xFF0F766E)),
      _ToolItem(Icons.category_rounded, 'Shapes', 'Design primitives', onShape, const Color(0xFF7C3AED)),
      _ToolItem(Icons.grid_4x4_rounded, 'Table', 'Rows & columns', onTable, const Color(0xFF0D9488)),
      _ToolItem(Icons.layers_rounded, 'Layers', 'Organize objects', onLayers, const Color(0xFF475569)),
      _ToolItem(Icons.auto_fix_high_rounded, 'Effects', 'Border & shadow', onEffects, const Color(0xFFDB2777)),
      _ToolItem(Icons.wallpaper_rounded, 'Background', 'Canvas background', onBackground, const Color(0xFFEA580C)),
      _ToolItem(Icons.dashboard_customize_rounded, 'Pages', 'Multi-page studio', onPages, const Color(0xFF4F46E5)),
      if (onImageStudio != null) _ToolItem(Icons.tune_rounded, 'Image Studio', 'Crop & fit', onImageStudio!, const Color(0xFF0891B2)),
      if (onAiStudio != null) _ToolItem(Icons.auto_awesome_rounded, 'AI Studio', 'Write • Image • Magic', onAiStudio!, const Color(0xFF6D28D9)),
      _ToolItem(Icons.ios_share_rounded, 'Export', 'PNG / JPG / PDF', onExport, const Color(0xFF16A34A)),
    ];
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(18, 8, 18, 20),
        child: Column(mainAxisSize: MainAxisSize.min, children: [
          Row(children: [
            const Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text('NaqshKaar Studio', style: TextStyle(fontSize: 21, fontWeight: FontWeight.w900)), SizedBox(height: 3), Text('All core design tools in one place', style: TextStyle(color: Colors.black54, fontSize: 12))])),
            IconButton(onPressed: () => Navigator.pop(context), icon: const Icon(Icons.close_rounded)),
          ]),
          const SizedBox(height: 10),
          Flexible(child: GridView.builder(shrinkWrap: true, itemCount: items.length, gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount: 3, mainAxisSpacing: 12, crossAxisSpacing: 12, childAspectRatio: .92), itemBuilder: (_, i) {
            final item = items[i];
            return Material(color: Colors.white, borderRadius: BorderRadius.circular(20), child: InkWell(borderRadius: BorderRadius.circular(20), onTap: () { Navigator.pop(context); item.onTap(); }, child: Container(decoration: BoxDecoration(borderRadius: BorderRadius.circular(20), border: Border.all(color: const Color(0xFFE5E7EB))), padding: const EdgeInsets.fromLTRB(8, 10, 8, 8), child: Column(children: [Container(width: 48, height: 48, decoration: BoxDecoration(color: item.color.withValues(alpha: .12), borderRadius: BorderRadius.circular(15)), child: Icon(item.icon, color: item.color, size: 26)), const SizedBox(height: 8), Text(item.title, textAlign: TextAlign.center, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w900)), const SizedBox(height: 2), Text(item.subtitle, textAlign: TextAlign.center, maxLines: 2, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 9, color: Colors.black54))]))));
          }))
        ]),
      ),
    );
  }
}

class _ToolItem {
  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback onTap;
  final Color color;
  const _ToolItem(this.icon, this.title, this.subtitle, this.onTap, this.color);
}