// Premium home shell retained while the editor receives the demo-inspired chrome upgrade.
// Release verification trigger: demo interface generator is enabled in CI.
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
  final ProjectRepository _repository = ProjectRepository();
  List<ProjectModel> _projects = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadProjects();
  }

  Future<void> _loadProjects() async {
    final projects = await _repository.list();
    if (!mounted) return;
    setState(() { _projects = projects; _loading = false; });
  }

  Future<void> _create(CanvasSize size) async {
    await Navigator.push(context, MaterialPageRoute(builder: (_) => WorkspaceScreen(size: size)));
    _loadProjects();
  }

  Future<void> _openProject(ProjectModel project) async {
    await Navigator.push(context, MaterialPageRoute(builder: (_) => WorkspaceScreen(initialProject: project)));
    _loadProjects();
  }

  Future<void> _customSize() async {
    final width = TextEditingController(text: '1200');
    final height = TextEditingController(text: '1200');
    final size = await showDialog<CanvasSize>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Custom Canvas'),
        content: Row(children: [
          Expanded(child: TextField(controller: width, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Width', suffixText: 'px'))),
          const SizedBox(width: 12),
          Expanded(child: TextField(controller: height, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Height', suffixText: 'px'))),
        ]),
        actions: [
          TextButton(onPressed: () => Navigator.pop(dialogContext), child: const Text('Cancel')),
          FilledButton(onPressed: () { final w = double.tryParse(width.text) ?? 1200; final h = double.tryParse(height.text) ?? 1200; Navigator.pop(dialogContext, CanvasSize(w.clamp(64, 8000), h.clamp(64, 8000))); }, child: const Text('Create')),
        ],
      ),
    );
    if (size != null) await _create(size);
  }

  Future<void> _deleteProject(ProjectModel project) async { await _repository.delete(project.id); _loadProjects(); }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Container(
          decoration: const BoxDecoration(gradient: LinearGradient(begin: Alignment.topLeft, end: Alignment.bottomRight, colors: [Color(0xFFF7F8FC), Color(0xFFEDE9FE)])),
          child: RefreshIndicator(
            onRefresh: _loadProjects,
            child: CustomScrollView(
              physics: const AlwaysScrollableScrollPhysics(),
              slivers: [
                SliverToBoxAdapter(child: Padding(padding: const EdgeInsets.fromLTRB(20, 18, 20, 10), child: _header())),
                SliverToBoxAdapter(child: Padding(padding: const EdgeInsets.fromLTRB(20, 12, 20, 20), child: _createCard())),
                if (_projects.isNotEmpty) ...[
                  SliverToBoxAdapter(child: Padding(padding: const EdgeInsets.symmetric(horizontal: 20), child: Row(children: [const Expanded(child: Text('Recent Projects', style: TextStyle(fontSize: 21, fontWeight: FontWeight.w900))), TextButton(onPressed: _showAllProjects, child: const Text('See all'))]))),
                  SliverToBoxAdapter(child: SizedBox(height: 150, child: ListView.separated(padding: const EdgeInsets.fromLTRB(20, 4, 20, 18), scrollDirection: Axis.horizontal, itemCount: _projects.take(6).length, separatorBuilder: (_, __) => const SizedBox(width: 12), itemBuilder: (_, i) => _projectCard(_projects[i])))),
                ],
                const SliverToBoxAdapter(child: Padding(padding: EdgeInsets.symmetric(horizontal: 20), child: Text('Quick Start', style: TextStyle(fontSize: 21, fontWeight: FontWeight.w900)))),
                SliverPadding(
                  padding: const EdgeInsets.fromLTRB(20, 12, 20, 30),
                  sliver: SliverGrid(
                    delegate: SliverChildListDelegate([
                      _quickCard(Icons.article_outlined, 'Urdu Post', '1080 × 1080', const CanvasSize(1080, 1080)),
                      _quickCard(Icons.phone_android_outlined, 'Story', '1080 × 1920', const CanvasSize(1080, 1920)),
                      _quickCard(Icons.image_outlined, 'Landscape', '1920 × 1080', const CanvasSize(1920, 1080)),
                      _quickCard(Icons.crop_square_outlined, 'Custom', 'Your own size', const CanvasSize(1200, 1200), custom: true),
                    ]),
                    gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount: 2, crossAxisSpacing: 14, mainAxisSpacing: 14, childAspectRatio: 1.12),
                  ),
                ),
                if (_loading) const SliverToBoxAdapter(child: Padding(padding: EdgeInsets.all(20), child: Center(child: CircularProgressIndicator()))),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _header() => Row(children: [
    Container(width: 52, height: 52, decoration: BoxDecoration(borderRadius: BorderRadius.circular(16), gradient: const LinearGradient(colors: [Color(0xFF7C3AED), Color(0xFF4F46E5)]), boxShadow: const [BoxShadow(blurRadius: 18, offset: Offset(0, 8), color: Color(0x337C3AED))]), child: const Center(child: Text('ن', textDirection: TextDirection.rtl, style: TextStyle(color: Colors.white, fontSize: 29, fontWeight: FontWeight.bold)))),
    const SizedBox(width: 14),
    const Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text('NaqshKaar Designer', style: TextStyle(fontSize: 22, fontWeight: FontWeight.w900, letterSpacing: -.5)), SizedBox(height: 3), Text('Professional Urdu design studio', style: TextStyle(color: Colors.black54, fontSize: 13))])),
    IconButton(onPressed: _showSettings, icon: const Icon(Icons.settings_outlined, size: 25)),
  ]);

  Widget _createCard() => Material(color: Colors.transparent, child: InkWell(borderRadius: BorderRadius.circular(26), onTap: () => _create(const CanvasSize(1080, 1080)), child: Ink(padding: const EdgeInsets.all(22), decoration: BoxDecoration(borderRadius: BorderRadius.circular(26), gradient: const LinearGradient(begin: Alignment.topLeft, end: Alignment.bottomRight, colors: [Color(0xFF7C3AED), Color(0xFF5B21B6)]), boxShadow: const [BoxShadow(blurRadius: 24, offset: Offset(0, 12), color: Color(0x447C3AED))]), child: Row(children: [Container(width: 58, height: 58, decoration: BoxDecoration(color: Colors.white.withValues(alpha: .16), borderRadius: BorderRadius.circular(18)), child: const Icon(Icons.add_rounded, color: Colors.white, size: 34)), const SizedBox(width: 16), const Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text('Create New Design', style: TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.w800)), SizedBox(height: 4), Text('Start with a professional blank canvas', style: TextStyle(color: Colors.white70, fontSize: 13))])), const Icon(Icons.arrow_forward_ios_rounded, color: Colors.white, size: 18)]))));

  Widget _quickCard(IconData icon, String title, String subtitle, CanvasSize size, {bool custom = false}) => Material(color: Colors.white, borderRadius: BorderRadius.circular(22), child: InkWell(borderRadius: BorderRadius.circular(22), onTap: custom ? _customSize : () => _create(size), child: Container(padding: const EdgeInsets.all(16), decoration: BoxDecoration(borderRadius: BorderRadius.circular(22), border: Border.all(color: const Color(0xFFE5E7EB))), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Container(width: 46, height: 46, decoration: BoxDecoration(color: const Color(0xFFF3E8FF), borderRadius: BorderRadius.circular(14)), child: Icon(icon, color: const Color(0xFF7C3AED), size: 25)), const Spacer(), Text(title, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800)), const SizedBox(height: 4), Text(subtitle, style: const TextStyle(fontSize: 12, color: Colors.black54))]))));

  Widget _projectCard(ProjectModel project) {
    return SizedBox(
      width: 240,
      child: Material(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
        child: InkWell(
          borderRadius: BorderRadius.circular(18),
          onTap: () => _openProject(project),
          onLongPress: () => _confirmDelete(project),
          child: Padding(
            padding: const EdgeInsets.all(14),
            child: Row(
              children: [
                Container(
                  width: 56,
                  height: 76,
                  decoration: BoxDecoration(
                    color: project.pages.first.background,
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: Colors.black12),
                  ),
                  child: Center(
                    child: Text(
                      '${project.pages.length}',
                      style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 20),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(project.name, maxLines: 2, overflow: TextOverflow.ellipsis, style: const TextStyle(fontWeight: FontWeight.w800)),
                      const SizedBox(height: 5),
                      Text('${project.pages.length} page${project.pages.length == 1 ? '' : 's'}', style: const TextStyle(fontSize: 12, color: Colors.black54)),
                      const SizedBox(height: 7),
                      const Text('Tap to continue • Hold to delete', style: TextStyle(fontSize: 10, color: Colors.black45)),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Future<void> _confirmDelete(ProjectModel project) async {
    final yes = await showDialog<bool>(context: context, builder: (c) => AlertDialog(title: const Text('Delete project?'), content: Text('Delete “${project.name}” permanently from this device?'), actions: [TextButton(onPressed: () => Navigator.pop(c, false), child: const Text('Cancel')), FilledButton(onPressed: () => Navigator.pop(c, true), child: const Text('Delete'))]));
    if (yes == true) await _deleteProject(project);
  }

  void _showAllProjects() {
    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      showDragHandle: true,
      builder: (c) => SafeArea(
        child: SizedBox(
          height: MediaQuery.sizeOf(c).height * .72,
          child: Column(
            children: [
              const Padding(
                padding: EdgeInsets.all(16),
                child: Text('Project Library', style: TextStyle(fontSize: 21, fontWeight: FontWeight.w900)),
              ),
              Expanded(
                child: _projects.isEmpty
                    ? const Center(child: Text('No saved projects yet.'))
                    : ListView.separated(
                        padding: const EdgeInsets.all(16),
                        itemCount: _projects.length,
                        separatorBuilder: (_, __) => const SizedBox(height: 8),
                        itemBuilder: (_, i) {
                          final p = _projects[i];
                          return ListTile(
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                            tileColor: const Color(0xFFF8F7FC),
                            leading: CircleAvatar(
                              backgroundColor: const Color(0xFFEDE9FE),
                              child: Text('${p.pages.length}'),
                            ),
                            title: Text(p.name, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontWeight: FontWeight.w800)),
                            subtitle: const Text('Tap to continue editing'),
                            onTap: () {
                              Navigator.pop(c);
                              _openProject(p);
                            },
                            trailing: IconButton(
                              onPressed: () => _confirmDelete(p),
                              icon: const Icon(Icons.delete_outline),
                            ),
                          );
                        },
                      ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showSettings() {
    showModalBottomSheet<void>(context: context, showDragHandle: true, builder: (c) => SafeArea(child: Column(mainAxisSize: MainAxisSize.min, children: [const ListTile(title: Text('NaqshKaar Designer', style: TextStyle(fontWeight: FontWeight.w900, fontSize: 19)), subtitle: Text('Professional Urdu Graphic Design Studio')), const ListTile(leading: Icon(Icons.font_download_outlined), title: Text('Urdu typography'), subtitle: Text('Gulzar + Noto Nastaliq Urdu bundled in release builds')), ListTile(leading: const Icon(Icons.folder_outlined), title: const Text('Project storage'), subtitle: Text('${_projects.length} saved project${_projects.length == 1 ? '' : 's'} on this device')), const SizedBox(height: 10)])));
  }
}
