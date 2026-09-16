import 'package:flutter/material.dart';
import '../data/project_repository.dart';
import '../models/design_models.dart';
import 'workspace_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _repo = ProjectRepository();
  List<ProjectModel> _projects = [];
  bool _loading = true;
  static const _blue = Color(0xFF2563EB);
  static const _navy = Color(0xFF101A35);
  static const _red = Color(0xFFFF1744);

  @override
  void initState() { super.initState(); _loadProjects(); }

  Future<void> _loadProjects() async {
    final items = await _repo.list();
    if (!mounted) return;
    setState(() { _projects = items; _loading = false; });
  }

  Future<void> _create(CanvasSize size) async {
    await Navigator.push(context, MaterialPageRoute(builder: (_) => WorkspaceScreen(size: size)));
    _loadProjects();
  }

  Future<void> _customSize() async {
    final w = TextEditingController(text: '1080');
    final h = TextEditingController(text: '1080');
    final result = await showDialog<CanvasSize>(context: context, builder: (c) => AlertDialog(
      title: const Text('Custom Canvas', style: TextStyle(fontWeight: FontWeight.w900)),
      content: Row(children: [
        Expanded(child: TextField(controller: w, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Width', suffixText: 'px'))),
        const SizedBox(width: 10),
        Expanded(child: TextField(controller: h, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Height', suffixText: 'px'))),
      ]),
      actions: [TextButton(onPressed: () => Navigator.pop(c), child: const Text('Cancel')), FilledButton(onPressed: () => Navigator.pop(c, CanvasSize((double.tryParse(w.text) ?? 1080).clamp(64, 16000), (double.tryParse(h.text) ?? 1080).clamp(64, 16000))), child: const Text('Create'))],
    ));
    w.dispose(); h.dispose();
    if (result != null) await _create(result);
  }

  Future<void> _openProject(ProjectModel p) async {
    await Navigator.push(context, MaterialPageRoute(builder: (_) => WorkspaceScreen(initialProject: p)));
    _loadProjects();
  }

  Future<void> _delete(ProjectModel p) async {
    final ok = await showDialog<bool>(context: context, builder: (c) => AlertDialog(
      title: const Text('Delete project?', style: TextStyle(fontWeight: FontWeight.w900)),
      content: Text('Delete “${p.name}” from this device?'),
      actions: [TextButton(onPressed: () => Navigator.pop(c, false), child: const Text('Cancel')), FilledButton(onPressed: () => Navigator.pop(c, true), child: const Text('Delete'))],
    ));
    if (ok == true) { await _repo.delete(p.id); _loadProjects(); }
  }

  void _feature(String title, IconData icon, Color color) {
    final size = title == 'Images' ? const CanvasSize(1200, 800) : const CanvasSize(1080, 1080);
    if (title == 'Urdu Fonts' || title == 'Text Editor') {
      _create(size);
    } else if (title == 'AI Design') {
      _create(size);
    } else {
      _create(size);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFF),
      body: SafeArea(child: RefreshIndicator(
        color: _blue,
        onRefresh: _loadProjects,
        child: CustomScrollView(physics: const AlwaysScrollableScrollPhysics(), slivers: [
          SliverToBoxAdapter(child: _header()),
          SliverToBoxAdapter(child: _hero()),
          SliverToBoxAdapter(child: _sectionTitle('Design Studio', 'Everything you need to create')),
          SliverPadding(padding: const EdgeInsets.fromLTRB(16, 0, 16, 8), sliver: SliverGrid.count(
            crossAxisCount: 4, mainAxisSpacing: 12, crossAxisSpacing: 10, childAspectRatio: .78,
            children: _features.map((f) => _featureTile(f)).toList(),
          )),
          SliverToBoxAdapter(child: _sectionTitle('Recent Projects', 'Continue where you left off', action: 'See all', onAction: _showAllProjects)),
          SliverToBoxAdapter(child: _projects.isEmpty ? _emptyRecent() : SizedBox(height: 154, child: ListView.separated(
            padding: const EdgeInsets.fromLTRB(16, 0, 16, 12), scrollDirection: Axis.horizontal, itemCount: _projects.take(6).length,
            separatorBuilder: (_, __) => const SizedBox(width: 12), itemBuilder: (_, i) => _projectCard(_projects[i]),
          ))),
          SliverToBoxAdapter(child: _proBanner()),
          const SliverToBoxAdapter(child: SizedBox(height: 88)),
        ]),
      )),
      bottomNavigationBar: _bottomBar(),
    );
  }

  final List<Map<String, dynamic>> _features = const [
    {'icon': Icons.add_rounded, 'title': 'New Design', 'sub': 'Blank Canvas', 'color': Color(0xFF2F80ED)},
    {'icon': Icons.auto_awesome_mosaic_rounded, 'title': 'Templates', 'sub': 'Ready Designs', 'color': Color(0xFF7C4DFF)},
    {'icon': Icons.text_fields_rounded, 'title': 'Text Editor', 'sub': 'Urdu & English', 'color': Color(0xFF0FAF78)},
    {'icon': Icons.font_download_rounded, 'title': 'Urdu Fonts', 'sub': 'Jameel & More', 'color': Color(0xFFE83E8C)},
    {'icon': Icons.category_rounded, 'title': 'Elements', 'sub': 'Shapes & Icons', 'color': Color(0xFFF59E0B)},
    {'icon': Icons.photo_library_rounded, 'title': 'Images', 'sub': 'Gallery', 'color': Color(0xFF0EA5E9)},
    {'icon': Icons.wallpaper_rounded, 'title': 'Backgrounds', 'sub': 'Colors & Texture', 'color': Color(0xFFEF476F)},
    {'icon': Icons.emoji_emotions_rounded, 'title': 'Stickers', 'sub': 'Urdu & Islamic', 'color': Color(0xFFB52DE3)},
    {'icon': Icons.layers_rounded, 'title': 'Layers', 'sub': 'Manage Layers', 'color': Color(0xFF0891B2)},
    {'icon': Icons.build_rounded, 'title': 'Tools', 'sub': 'Edit & Adjust', 'color': Color(0xFF64748B)},
    {'icon': Icons.smart_toy_rounded, 'title': 'AI Design', 'sub': 'Text to Design', 'color': Color(0xFF4F46E5), 'new': true},
    {'icon': Icons.auto_fix_high_rounded, 'title': 'Pro Effects', 'sub': 'Filters & FX', 'color': Color(0xFF00A99D)},
  ];

  Widget _header() => Padding(padding: const EdgeInsets.fromLTRB(16, 12, 16, 10), child: Row(children: [
    _roundButton(Icons.menu_rounded, () => _showMenu()),
    const SizedBox(width: 12),
    Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Row(children: [
        const Text('NaqshKaar', style: TextStyle(fontSize: 24, fontWeight: FontWeight.w900, color: _navy, letterSpacing: -.7)),
        const SizedBox(width: 5), Text('Designer', style: TextStyle(fontSize: 24, fontWeight: FontWeight.w900, color: Color(0xFFD49A19), letterSpacing: -.7)),
      ]),
      const Text('URDU DESIGNER APP', style: TextStyle(fontSize: 9.5, fontWeight: FontWeight.w800, letterSpacing: 2.2, color: Color(0xFF73809B))),
      const Text('نقشکار ڈیزائنر', textDirection: TextDirection.rtl, style: TextStyle(fontFamily: 'JameelNooriNastaleeq', fontSize: 20, height: .9, color: _navy)),
    ])),
    _roundButton(Icons.notifications_none_rounded, _showNotifications, badge: true),
  ]));

  Widget _roundButton(IconData icon, VoidCallback onTap, {bool badge = false}) => Stack(children: [Material(color: Colors.white, borderRadius: BorderRadius.circular(15), child: InkWell(onTap: onTap, borderRadius: BorderRadius.circular(15), child: SizedBox(width: 46, height: 46, child: Icon(icon, color: _navy, size: 25)))), if (badge) Positioned(right: 1, top: 1, child: Container(width: 10, height: 10, decoration: const BoxDecoration(color: _red, shape: BoxShape.circle))) ]);

  Widget _hero() => Padding(padding: const EdgeInsets.fromLTRB(16, 8, 16, 20), child: Container(
    height: 190, clipBehavior: Clip.antiAlias, decoration: BoxDecoration(
      borderRadius: BorderRadius.circular(28),
      gradient: const LinearGradient(begin: Alignment.topLeft, end: Alignment.bottomRight, colors: [Color(0xFFEAF3FF), Color(0xFFDDE8FF), Color(0xFFF9F0FF)]),
      border: Border.all(color: Colors.white, width: 1.5),
      boxShadow: const [BoxShadow(color: Color(0x183B65C9), blurRadius: 26, offset: Offset(0, 12))],
    ), child: Stack(children: [
      Positioned(right: -18, top: -30, child: _heroOrb(150, const Color(0x263B82F6))),
      Positioned(right: 12, bottom: -48, child: _heroOrb(120, const Color(0x20A855F7))),
      Padding(padding: const EdgeInsets.fromLTRB(20, 18, 8, 16), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        const Text('Design Without Limits', style: TextStyle(fontSize: 26, fontWeight: FontWeight.w900, color: _navy, height: 1.05)),
        const SizedBox(height: 7),
        const Text('اپنے خیال کو خوبصورت ڈیزائن میں بدلیں', textDirection: TextDirection.rtl, style: TextStyle(fontFamily: 'JameelNooriNastaleeq', fontSize: 23, color: _navy, height: 1.0)),
        const SizedBox(height: 6),
        const Text('Beautiful Urdu Text  •  Professional Graphics', style: TextStyle(fontSize: 11.5, color: Color(0xFF52627F), fontWeight: FontWeight.w600)),
        const Spacer(),
        Material(color: Colors.transparent, child: InkWell(onTap: () => _create(const CanvasSize(1080, 1080)), borderRadius: BorderRadius.circular(16), child: Ink(
          padding: const EdgeInsets.symmetric(horizontal: 17, vertical: 11), decoration: BoxDecoration(borderRadius: BorderRadius.circular(16), gradient: const LinearGradient(colors: [Color(0xFF2563EB), Color(0xFF4F46E5)]), boxShadow: const [BoxShadow(color: Color(0x382563EB), blurRadius: 13, offset: Offset(0, 7))]),
          child: const Row(mainAxisSize: MainAxisSize.min, children: [Text('Start Designing', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w900, fontSize: 14)), SizedBox(width: 8), Icon(Icons.arrow_forward_rounded, color: Colors.white, size: 19)]),
        ))),
      ])),
      Positioned(right: 14, top: 34, child: Transform.rotate(angle: -.10, child: Container(width: 108, height: 116, padding: const EdgeInsets.all(8), decoration: BoxDecoration(color: const Color(0xFFFDFBF4), borderRadius: BorderRadius.circular(13), border: Border.all(color: const Color(0xFFE6D7AE)), boxShadow: const [BoxShadow(color: Color(0x22303B5C), blurRadius: 13, offset: Offset(0, 8))]), child: const Column(mainAxisAlignment: MainAxisAlignment.center, children: [Text('بِسْمِ اللّٰهِ', textDirection: TextDirection.rtl, style: TextStyle(fontFamily: 'JameelNooriNastaleeq', fontSize: 18, color: Color(0xFF172B4D))), SizedBox(height: 4), Text('نقشکار', textDirection: TextDirection.rtl, style: TextStyle(fontFamily: 'JameelNooriNastaleeq', fontSize: 25, color: Color(0xFFB8860B))), SizedBox(height: 2), Text('Create • Edit • Export', style: TextStyle(fontSize: 7, color: Color(0xFF6B7280)))]))),
    ])));

  Widget _heroOrb(double size, Color color) => Container(width: size, height: size, decoration: BoxDecoration(shape: BoxShape.circle, color: color));

  Widget _sectionTitle(String title, String subtitle, {String? action, VoidCallback? onAction}) => Padding(padding: const EdgeInsets.fromLTRB(18, 2, 16, 12), child: Row(crossAxisAlignment: CrossAxisAlignment.end, children: [Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(title, style: const TextStyle(fontSize: 19, fontWeight: FontWeight.w900, color: _navy)), const SizedBox(height: 2), Text(subtitle, style: const TextStyle(fontSize: 11, color: Color(0xFF7A879F)))])), if (action != null) TextButton(onPressed: onAction, child: Text(action, style: const TextStyle(fontWeight: FontWeight.w800, color: _blue)))]));

  Widget _featureTile(Map<String, dynamic> f) {
    final color = f['color'] as Color;
    final title = f['title'] as String;
    return Stack(clipBehavior: Clip.none, children: [Material(color: Colors.white, borderRadius: BorderRadius.circular(18), child: InkWell(onTap: () => title == 'New Design' ? _create(const CanvasSize(1080, 1080)) : _feature(title, f['icon'] as IconData, color), borderRadius: BorderRadius.circular(18), child: Container(
      decoration: BoxDecoration(borderRadius: BorderRadius.circular(18), border: Border.all(color: const Color(0xFFE8ECF4)), boxShadow: const [BoxShadow(color: Color(0x0D172B4D), blurRadius: 10, offset: Offset(0, 4))]),
      padding: const EdgeInsets.fromLTRB(4, 9, 4, 6), child: Column(children: [
        Container(width: 48, height: 48, decoration: BoxDecoration(shape: BoxShape.circle, color: color.withValues(alpha: .10)), child: Icon(f['icon'] as IconData, color: color, size: 25)),
        const SizedBox(height: 6), Text(title, maxLines: 1, overflow: TextOverflow.ellipsis, textAlign: TextAlign.center, style: const TextStyle(fontSize: 10.5, fontWeight: FontWeight.w900, color: _navy)),
        const SizedBox(height: 1), Text(f['sub'] as String, maxLines: 1, overflow: TextOverflow.ellipsis, textAlign: TextAlign.center, style: const TextStyle(fontSize: 7.5, color: Color(0xFF7C889F))),
      ]))), if (f['new'] == true) Positioned(right: -4, top: -7, child: Container(padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 3), decoration: BoxDecoration(color: _red, borderRadius: BorderRadius.circular(9), boxShadow: const [BoxShadow(color: Color(0x333F1020), blurRadius: 5)]), child: const Text('NEW', style: TextStyle(color: Colors.white, fontSize: 7.5, fontWeight: FontWeight.w900))))]);
  }

  Widget _emptyRecent() => Padding(padding: const EdgeInsets.fromLTRB(16, 0, 16, 10), child: Material(color: Colors.white, borderRadius: BorderRadius.circular(18), child: InkWell(onTap: () => _create(const CanvasSize(1080, 1080)), borderRadius: BorderRadius.circular(18), child: Container(height: 92, decoration: BoxDecoration(borderRadius: BorderRadius.circular(18), border: Border.all(color: const Color(0xFFE7EBF3))), child: const Row(mainAxisAlignment: MainAxisAlignment.center, children: [Icon(Icons.add_circle_outline_rounded, color: _blue), SizedBox(width: 9), Text('Create your first design', style: TextStyle(fontWeight: FontWeight.w800, color: _navy))]))));

  Widget _projectCard(ProjectModel p) => SizedBox(width: 190, child: Material(color: Colors.white, borderRadius: BorderRadius.circular(17), child: InkWell(onTap: () => _openProject(p), onLongPress: () => _delete(p), borderRadius: BorderRadius.circular(17), child: Padding(padding: const EdgeInsets.all(9), child: Row(children: [Container(width: 58, height: 92, decoration: BoxDecoration(color: p.pages.isEmpty ? Colors.white : p.pages.first.background, borderRadius: BorderRadius.circular(11), border: Border.all(color: const Color(0xFFE6EAF2))), child: Center(child: Text('${p.pages.length}', style: const TextStyle(fontSize: 19, fontWeight: FontWeight.w900, color: _navy)))), const SizedBox(width: 10), Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, mainAxisAlignment: MainAxisAlignment.center, children: [Text(p.name, maxLines: 2, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 12.5, fontWeight: FontWeight.w900, color: _navy)), const SizedBox(height: 5), Text('${p.pages.length} page${p.pages.length == 1 ? '' : 's'}', style: const TextStyle(fontSize: 10, color: Color(0xFF7A879F))), const SizedBox(height: 7), const Text('Tap to edit', style: TextStyle(fontSize: 9, color: _blue, fontWeight: FontWeight.w700))]))]))));

  Widget _proBanner() => Padding(padding: const EdgeInsets.fromLTRB(16, 12, 16, 16), child: Material(color: Colors.transparent, borderRadius: BorderRadius.circular(20), child: InkWell(onTap: () => _showPro(), borderRadius: BorderRadius.circular(20), child: Ink(decoration: BoxDecoration(borderRadius: BorderRadius.circular(20), gradient: const LinearGradient(colors: [Color(0xFFFFF7D8), Color(0xFFFFE9A6)]), border: Border.all(color: const Color(0xFFEACD75)), boxShadow: const [BoxShadow(color: Color(0x1AB88B16), blurRadius: 14, offset: Offset(0, 6))]), padding: const EdgeInsets.symmetric(horizontal: 15, vertical: 13), child: const Row(children: [Icon(Icons.workspace_premium_rounded, color: Color(0xFFB78300), size: 36), SizedBox(width: 10), Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text('NaqshKaar Pro', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w900, color: _navy)), Text('Premium templates  •  Fonts  •  AI  •  Effects', style: TextStyle(fontSize: 9.5, color: Color(0xFF7B6941)))])), Icon(Icons.arrow_forward_rounded, color: Color(0xFFB78300))])))));

  Widget _bottomBar() => SafeArea(top: false, child: Container(height: 72, decoration: const BoxDecoration(color: Colors.white, boxShadow: [BoxShadow(color: Color(0x18000000), blurRadius: 20, offset: Offset(0, -5))]), child: Stack(alignment: Alignment.topCenter, children: [Row(children: [Expanded(child: _navItem(Icons.home_rounded, 'Home', true, () {})), Expanded(child: _navItem(Icons.folder_rounded, 'Projects', false, _showAllProjects)), const SizedBox(width: 76), Expanded(child: _navItem(Icons.school_rounded, 'Learn', false, _showLearn)), Expanded(child: _navItem(Icons.person_rounded, 'Profile', false, _showProfile))]), Positioned(top: -25, child: GestureDetector(onTap: () => _create(const CanvasSize(1080, 1080)), child: Container(width: 66, height: 66, decoration: BoxDecoration(shape: BoxShape.circle, gradient: const LinearGradient(begin: Alignment.topLeft, end: Alignment.bottomRight, colors: [Color(0xFFFF4B5F), Color(0xFFFF003B), Color(0xFFD90032)]), border: Border.all(color: Colors.white, width: 4), boxShadow: const [BoxShadow(color: Color(0x66FF1744), blurRadius: 24, spreadRadius: 5, offset: Offset(0, 8)), BoxShadow(color: Color(0x44FF1744), blurRadius: 7, offset: Offset(0, 2))]), child: const Icon(Icons.add_rounded, color: Colors.white, size: 39))))]));

  Widget _navItem(IconData icon, String label, bool active, VoidCallback onTap) => Expanded(child: InkWell(onTap: onTap, child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [Icon(icon, size: 24, color: active ? _blue : const Color(0xFF9AA6BB)), const SizedBox(height: 2), Text(label, style: TextStyle(fontSize: 9.5, fontWeight: FontWeight.w800, color: active ? _blue : const Color(0xFF9AA6BB)))])));

  void _showAllProjects() => showModalBottomSheet<void>(context: context, isScrollControlled: true, showDragHandle: true, builder: (c) => SafeArea(child: SizedBox(height: MediaQuery.sizeOf(c).height * .78, child: Column(children: [const Padding(padding: EdgeInsets.fromLTRB(18, 8, 18, 12), child: Text('Project Library', style: TextStyle(fontSize: 21, fontWeight: FontWeight.w900, color: _navy))), Expanded(child: _projects.isEmpty ? const Center(child: Text('No saved projects yet.')) : ListView.separated(padding: const EdgeInsets.all(16), itemCount: _projects.length, separatorBuilder: (_, __) => const SizedBox(height: 8), itemBuilder: (_, i) { final p = _projects[i]; return ListTile(shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)), tileColor: const Color(0xFFF7F9FD), leading: CircleAvatar(backgroundColor: const Color(0xFFEAF1FF), child: Text('${p.pages.length}', style: const TextStyle(fontWeight: FontWeight.w900))), title: Text(p.name, style: const TextStyle(fontWeight: FontWeight.w800)), subtitle: const Text('Tap to continue editing'), onTap: () { Navigator.pop(c); _openProject(p); }, trailing: IconButton(onPressed: () => _delete(p), icon: const Icon(Icons.delete_outline_rounded))); }))])));

  void _showMenu() => showModalBottomSheet<void>(context: context, showDragHandle: true, builder: (c) => SafeArea(child: Column(mainAxisSize: MainAxisSize.min, children: [const ListTile(title: Text('NaqshKaar Designer', style: TextStyle(fontWeight: FontWeight.w900, fontSize: 19)), subtitle: Text('Professional Urdu Graphic Design Studio')), ListTile(leading: const Icon(Icons.add_box_outlined), title: const Text('New Design'), onTap: () { Navigator.pop(c); _create(const CanvasSize(1080, 1080)); }), ListTile(leading: const Icon(Icons.photo_library_outlined), title: const Text('Projects'), onTap: () { Navigator.pop(c); _showAllProjects(); }), ListTile(leading: const Icon(Icons.settings_outlined), title: const Text('Settings'), onTap: () { Navigator.pop(c); _showProfile(); }), const SizedBox(height: 8)])));
  void _showNotifications() => _toast('Notifications will appear here.');
  void _showLearn() => _toast('Learn: Urdu typography, layouts and export tips.');
  void _showProfile() => _showSettings();
  void _showPro() => _toast('Pro features are connected to the designer workspace.');
  void _toast(String text) => ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(text)));
  void _showSettings() => showModalBottomSheet<void>(context: context, showDragHandle: true, builder: (c) => SafeArea(child: Column(mainAxisSize: MainAxisSize.min, children: [const ListTile(title: Text('NaqshKaar Designer', style: TextStyle(fontWeight: FontWeight.w900, fontSize: 19)), subtitle: Text('Light premium workspace')), ListTile(leading: const Icon(Icons.font_download_outlined), title: const Text('Jameel Noori Nastaleeq'), subtitle: const Text('Primary Urdu display font')), ListTile(leading: const Icon(Icons.folder_outlined), title: const Text('Local projects'), subtitle: Text('${_projects.length} saved project${_projects.length == 1 ? '' : 's'}')), const SizedBox(height: 10)])));
}
