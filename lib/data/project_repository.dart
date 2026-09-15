import 'dart:convert';
import 'dart:io';
import 'package:path_provider/path_provider.dart';
import '../models/design_models.dart';

class ProjectRepository {
  Future<Directory> _dir() async {
    final base = await getApplicationDocumentsDirectory();
    final dir = Directory('${base.path}/naqshkaar/projects');
    if (!await dir.exists()) await dir.create(recursive: true);
    return dir;
  }

  Future<File> _file(String id) async => File('${(await _dir()).path}/$id.json');

  /// Crash-safe save: write the complete project to a temporary file first,
  /// flush it, then replace the previous snapshot. This prevents a partially
  /// written JSON project from becoming the user's only recovery copy.
  Future<void> save(ProjectModel project) async {
    final file = await _file(project.id);
    final temp = File('${file.path}.tmp');
    try {
      await temp.writeAsString(jsonEncode(project.toJson()), flush: true);
      if (await file.exists()) await file.delete();
      await temp.rename(file.path);
    } catch (_) {
      if (await temp.exists()) {
        try { await temp.delete(); } catch (_) {}
      }
      rethrow;
    }
  }

  Future<ProjectModel?> load(String id) async {
    final file = await _file(id);
    if (!await file.exists()) return null;
    try {
      final raw = jsonDecode(await file.readAsString());
      if (raw is! Map) return null;
      return ProjectModel.fromJson(Map<String, dynamic>.from(raw));
    } catch (_) { return null; }
  }

  Future<List<ProjectModel>> list() async {
    final dir = await _dir();
    final result = <ProjectModel>[];
    await for (final entity in dir.list()) {
      if (entity is! File || !entity.path.endsWith('.json')) continue;
      try {
        final raw = jsonDecode(await entity.readAsString());
        if (raw is Map) result.add(ProjectModel.fromJson(Map<String, dynamic>.from(raw)));
      } catch (_) {}
    }
    result.sort((a, b) => b.lastModified.compareTo(a.lastModified));
    return result;
  }

  Future<void> delete(String id) async {
    final file = await _file(id);
    if (await file.exists()) await file.delete();
  }
}
