import 'dart:typed_data';
import 'package:flutter/material.dart';
import '../models/design_models.dart';

class WorkspaceController extends ChangeNotifier {
  static int _idCounter = 0;
  final List<ProjectModel> _history = [];
  final List<ProjectModel> _future = [];
  late ProjectModel project;
  int currentPageIndex = 0;
  String? selectedId;

  WorkspaceController({ProjectModel? initial, CanvasSize? newSize}) {
    project = initial ?? ProjectModel(
      id: _newId('project'),
      name: 'NaqshKaar Design',
      pages: [
        DesignPage(
          title: 'Page 1',
          size: newSize ?? const CanvasSize(1080, 1080),
        ),
      ],
    );

    if (project.pages.isEmpty) {
      project.pages.add(
        DesignPage(
          title: 'Page 1',
          size: newSize ?? const CanvasSize(1080, 1080),
        ),
      );
    }

    currentPageIndex = 0;
  }

  DesignPage get page => project.pages[currentPageIndex];

  List<DesignElement> get elements => page.elements;

  static String _newId(String prefix) {
    _idCounter++;
    return '${prefix}_${DateTime.now().microsecondsSinceEpoch}_$_idCounter';
  }

  void _checkpoint() {
    _history.add(ProjectModel.fromJson(project.toJson()));

    if (_history.length > 30) {
      _history.removeAt(0);
    }

    _future.clear();
  }

  void _changed() {
    project.lastModified = DateTime.now().millisecondsSinceEpoch;
    notifyListeners();
  }

  bool get canUndo => _history.isNotEmpty;

  bool get canRedo => _future.isNotEmpty;

  void undo() {
    if (!canUndo) return;

    _future.add(
      ProjectModel.fromJson(project.toJson()),
    );

    project = _history.removeLast();

    currentPageIndex =
        currentPageIndex.clamp(0, project.pages.length - 1);

    selectedId = null;

    notifyListeners();
  }

  void redo() {
    if (!canRedo) return;

    _history.add(
      ProjectModel.fromJson(project.toJson()),
    );

    project = _future.removeLast();

    currentPageIndex =
        currentPageIndex.clamp(0, project.pages.length - 1);

    selectedId = null;

    notifyListeners();
  }

  void select(String? id) {
    selectedId = id;
    notifyListeners();
  }

  DesignElement addText({
    String text = 'اپنا متن یہاں لکھیں',
    bool rtl = true,
  }) {
    _checkpoint();

    final e = DesignElement(
      id: _newId('text'),
      kind: ElementKind.text,
      x: page.size.width * .1,
      y: page.size.height * .35,
      width: page.size.width * .8,
      height: 150,
      text: text,
      fontSize: 64,
      textDirection:
          rtl ? TextDirection.rtl : TextDirection.ltr,
    );

    page.elements.add(e);
    selectedId = e.id;
    _changed();

    return e;
  }

  DesignElement addShape() {
    _checkpoint();

    final e = DesignElement(
      id: _newId('shape'),
      kind: ElementKind.shape,
      x: page.size.width * .35,
      y: page.size.height * .3,
      width: 320,
      height: 220,
      colorValue: const Color(0xFF7C3AED).toARGB32(),
    );

    page.elements.add(e);
    selectedId = e.id;
    _changed();

    return e;
  }

  DesignElement addImage(Uint8List bytes) {
    _checkpoint();

    final e = DesignElement(
      id: _newId('image'),
      kind: ElementKind.image,
      x: page.size.width * .15,
      y: page.size.height * .2,
      width: page.size.width * .7,
      height: page.size.height * .45,
      imageBytes: bytes,
    );

    page.elements.add(e);
    selectedId = e.id;
    _changed();

    return e;
  }

  void updateSelected({
    double? x,
    double? y,
    double? width,
    double? height,
    double? rotation,
    double? opacity,
    int? colorValue,
  }) {
    final e = selected;

    if (e == null || e.locked) return;

    _checkpoint();

    if (x != null) e.x = x;
    if (y != null) e.y = y;

    if (width != null) {
      e.width = width.clamp(
        20,
        page.size.width * 2,
      );
    }

    if (height != null) {
      e.height = height.clamp(
        20,
        page.size.height * 2,
      );
    }

    if (rotation != null) {
      e.rotation = rotation;
    }

    if (opacity != null) {
      e.opacity = opacity.clamp(0, 1);
    }

    if (colorValue != null) {
      e.colorValue = colorValue;
    }

    _changed();
  }

  DesignElement? get selected =>
      selectedId == null
          ? null
          : elements
              .where((e) => e.id == selectedId)
              .firstOrNull;

  void deleteSelected() {
    final id = selectedId;

    if (id == null) return;

    final index =
        elements.indexWhere((e) => e.id == id);

    if (index < 0) return;

    _checkpoint();

    elements.removeAt(index);
    selectedId = null;

    _changed();
  }

  void duplicateSelected() {
    final e = selected;

    if (e == null) return;

    _checkpoint();

    final copy = e.clone()
      ..id = _newId('element');

    copy.x += 24;
    copy.y += 24;

    elements.add(copy);
    selectedId = copy.id;

    _changed();
  }

  void setBackground(Color color) {
    _checkpoint();

    page.background = color;

    _changed();
  }

  void resizeCanvas(
    double width,
    double height,
  ) {
    if (width < 64 || height < 64) return;

    _checkpoint();

    final old = page.size;

    final sx = width / old.width;
    final sy = height / old.height;

    page.size = CanvasSize(width, height);

    for (final e in elements) {
      e.x *= sx;
      e.y *= sy;
      e.width *= sx;
      e.height *= sy;
    }

    _changed();
  }

  void addPage() {
    _checkpoint();

    project.pages.add(
      DesignPage(
        title: 'Page ${project.pages.length + 1}',
        size: page.size,
      ),
    );

    currentPageIndex =
        project.pages.length - 1;

    selectedId = null;

    _changed();
  }

  void duplicatePage() {
    _checkpoint();

    final copy = page.clone()
      ..title = '${page.title} Copy';

    project.pages.insert(
      currentPageIndex + 1,
      copy,
    );

    currentPageIndex++;
    selectedId = null;

    _changed();
  }

  void deletePage() {
    if (project.pages.length <= 1) return;

    _checkpoint();

    project.pages.removeAt(currentPageIndex);

    currentPageIndex =
        currentPageIndex.clamp(
      0,
      project.pages.length - 1,
    );

    selectedId = null;

    _changed();
  }

  void switchPage(int index) {
    if (index < 0 ||
        index >= project.pages.length) {
      return;
    }

    currentPageIndex = index;
    selectedId = null;

    notifyListeners();
  }
}
