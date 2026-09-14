import 'dart:math' as math;
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
  bool _continuousCheckpointActive = false;

  WorkspaceController({ProjectModel? initial, CanvasSize? newSize}) {
    project = initial ?? ProjectModel(id: _newId('project'), name: 'NaqshKaar Design', pages: [DesignPage(title: 'Page 1', size: newSize ?? const CanvasSize(1080, 1080))]);
    if (project.pages.isEmpty) project.pages.add(DesignPage(title: 'Page 1', size: newSize ?? const CanvasSize(1080, 1080)));
  }

  DesignPage get page => project.pages[currentPageIndex];
  List<DesignElement> get elements => page.elements;
  static String _newId(String prefix) { _idCounter++; return '${prefix}_${DateTime.now().microsecondsSinceEpoch}_$_idCounter'; }
  void _checkpoint() { _history.add(ProjectModel.fromJson(project.toJson())); if (_history.length > 30) _history.removeAt(0); _future.clear(); }
  void _changed() { project.lastModified = DateTime.now().millisecondsSinceEpoch; notifyListeners(); }
  bool get canUndo => _history.isNotEmpty;
  bool get canRedo => _future.isNotEmpty;
  void undo() { if (!canUndo) return; _future.add(ProjectModel.fromJson(project.toJson())); project = _history.removeLast(); currentPageIndex = currentPageIndex.clamp(0, project.pages.length - 1); selectedId = null; _changed(); }
  void redo() { if (!canRedo) return; _history.add(ProjectModel.fromJson(project.toJson())); project = _future.removeLast(); currentPageIndex = currentPageIndex.clamp(0, project.pages.length - 1); selectedId = null; _changed(); }
  void select(String? id) { selectedId = id; notifyListeners(); }

  DesignElement addText({String text = 'اپنا متن یہاں لکھیں', bool rtl = true}) { _checkpoint(); final e = DesignElement(id: _newId('text'), kind: ElementKind.text, x: page.size.width * .1, y: page.size.height * .35, width: page.size.width * .8, height: 180, text: text, fontSize: 64, textDirection: rtl ? TextDirection.rtl : TextDirection.ltr); page.elements.add(e); selectedId = e.id; _changed(); return e; }
  DesignElement addShape() { _checkpoint(); final e = DesignElement(id: _newId('shape'), kind: ElementKind.shape, x: page.size.width * .35, y: page.size.height * .3, width: 320, height: 220, colorValue: const Color(0xFF7C3AED).toARGB32()); page.elements.add(e); selectedId = e.id; _changed(); return e; }
  DesignElement addImage(Uint8List bytes) { _checkpoint(); final e = DesignElement(id: _newId('image'), kind: ElementKind.image, x: page.size.width * .15, y: page.size.height * .2, width: page.size.width * .7, height: page.size.height * .45, imageBytes: bytes); page.elements.add(e); selectedId = e.id; _changed(); return e; }
  void replaceSelectedImage(Uint8List bytes) { final e = selected; if (e == null || e.kind != ElementKind.image || e.locked) return; _checkpoint(); e.imageBytes = bytes; _changed(); }

  void updateSelected({double? x, double? y, double? width, double? height, double? rotation, double? opacity, int? colorValue}) { final e = selected; if (e == null || e.locked) return; _checkpoint(); if (x != null) e.x = x; if (y != null) e.y = y; if (width != null) e.width = width.clamp(20, page.size.width * 2); if (height != null) e.height = height.clamp(20, page.size.height * 2); if (rotation != null) e.rotation = rotation; if (opacity != null) e.opacity = opacity.clamp(0, 1); if (colorValue != null) e.colorValue = colorValue; _changed(); }
  void setSelectedOpacity(double value) => updateSelected(opacity: value.clamp(0, 1));
  void resetSelectedRotation() => updateSelected(rotation: 0);
  void setSelectedRadius(double value) { final e = selected; if (e == null || e.kind != ElementKind.shape || e.locked) return; _checkpoint(); e.radius = value.clamp(0, 240); _changed(); }
  void setSelectedStroke({required double width, required int colorValue}) { final e = selected; if (e == null || e.locked) return; _checkpoint(); e.strokeWidth = width.clamp(0, 40); e.strokeColorValue = colorValue; _changed(); }
  void setSelectedShadow({required double blur, required double offsetX, required double offsetY, required int colorValue}) { final e = selected; if (e == null || e.locked) return; _checkpoint(); e.shadowBlur = blur.clamp(0, 80); e.shadowOffsetX = offsetX.clamp(-100, 100); e.shadowOffsetY = offsetY.clamp(-100, 100); e.shadowColorValue = colorValue; _changed(); }
  void setSelectedTypography({double? letterSpacing, double? lineHeight}) { final e = selected; if (e == null || e.kind != ElementKind.text || e.locked) return; _checkpoint(); if (letterSpacing != null) e.letterSpacing = letterSpacing.clamp(-10, 20); if (lineHeight != null) e.lineHeight = lineHeight.clamp(.7, 3); _changed(); }

  void centerSelected() { final e = selected; if (e == null || e.locked) return; _checkpoint(); e.x = (page.size.width - e.width) / 2; e.y = (page.size.height - e.height) / 2; _changed(); }
  void startContinuousEdit() { if (_continuousCheckpointActive) return; final e = selected; if (e == null || e.locked) return; _checkpoint(); _continuousCheckpointActive = true; }
  void moveSelectedBy(double dx, double dy) { final e = selected; if (e == null || e.locked) return; e.x = (e.x + dx).clamp(-e.width * .75, page.size.width - e.width * .25); e.y = (e.y + dy).clamp(-e.height * .75, page.size.height - e.height * .25); _changed(); }
  void resizeSelectedFromHandle(String handle, double dx, double dy) { final e = selected; if (e == null || e.locked) return; final c = math.cos(e.rotation), s = math.sin(e.rotation); final localDx = dx * c + dy * s, localDy = -dx * s + dy * c; const minSize = 32.0; double newWidth = e.width, newHeight = e.height; if (handle.contains('right')) newWidth += localDx; if (handle.contains('left')) newWidth -= localDx; if (handle.contains('bottom')) newHeight += localDy; if (handle.contains('top')) newHeight -= localDy; newWidth = newWidth.clamp(minSize, page.size.width * 2); newHeight = newHeight.clamp(minSize, page.size.height * 2); final shiftX = handle.contains('left') ? e.width - newWidth : 0.0; final shiftY = handle.contains('top') ? e.height - newHeight : 0.0; e.x += shiftX * c - shiftY * s; e.y += shiftX * s + shiftY * c; e.width = newWidth; e.height = newHeight; _changed(); }
  void rotateSelectedTo(double angle) { final e = selected; if (e == null || e.locked) return; e.rotation = angle; _changed(); }
  void finishContinuousEdit() { _continuousCheckpointActive = false; notifyListeners(); }

  void editSelectedText(String value) { final e = selected; if (e == null || e.kind != ElementKind.text || e.locked) return; _checkpoint(); e.text = value; _changed(); }
  void setSelectedFontSize(double value) { final e = selected; if (e == null || e.kind != ElementKind.text || e.locked) return; _checkpoint(); e.fontSize = value.clamp(8, 300); _changed(); }
  void setSelectedFont(String family) { final e = selected; if (e == null || e.kind != ElementKind.text || e.locked) return; _checkpoint(); e.fontFamily = family; _changed(); }
  void toggleSelectedBold() { final e = selected; if (e == null || e.kind != ElementKind.text || e.locked) return; _checkpoint(); e.bold = !e.bold; _changed(); }
  void toggleSelectedItalic() { final e = selected; if (e == null || e.kind != ElementKind.text || e.locked) return; _checkpoint(); e.italic = !e.italic; _changed(); }
  void setSelectedAlign(TextAlign align) { final e = selected; if (e == null || e.kind != ElementKind.text || e.locked) return; _checkpoint(); e.textAlign = align; _changed(); }
  void setSelectedDirection(TextDirection direction) { final e = selected; if (e == null || e.kind != ElementKind.text || e.locked) return; _checkpoint(); e.textDirection = direction; _changed(); }
  void toggleSelectedLock() { final e = selected; if (e == null) return; _checkpoint(); e.locked = !e.locked; _changed(); }
  void toggleSelectedHidden() { final e = selected; if (e == null) return; _checkpoint(); e.hidden = !e.hidden; _changed(); }
  void bringSelectedToFront() { final e = selected; if (e == null) return; final i = elements.indexOf(e); if (i < 0 || i == elements.length - 1) return; _checkpoint(); elements.removeAt(i); elements.add(e); _changed(); }
  void sendSelectedToBack() { final e = selected; if (e == null) return; final i = elements.indexOf(e); if (i <= 0) return; _checkpoint(); elements.removeAt(i); elements.insert(0, e); _changed(); }
  void bringSelectedForward() { final e = selected; if (e == null || e.locked) return; final i = elements.indexOf(e); if (i < 0 || i >= elements.length - 1) return; _checkpoint(); final next = elements.removeAt(i); elements.insert(i + 1, next); _changed(); }
  void sendSelectedBackward() { final e = selected; if (e == null || e.locked) return; final i = elements.indexOf(e); if (i <= 0) return; _checkpoint(); final current = elements.removeAt(i); elements.insert(i - 1, current); _changed(); }
  DesignElement? get selected => selectedId == null ? null : elements.where((e) => e.id == selectedId).firstOrNull;
  void deleteSelected() { final id = selectedId; if (id == null) return; final i = elements.indexWhere((e) => e.id == id); if (i < 0) return; _checkpoint(); elements.removeAt(i); selectedId = null; _changed(); }
  void duplicateSelected() { final e = selected; if (e == null) return; _checkpoint(); final copy = e.clone()..id = _newId('element'); copy.x += 24; copy.y += 24; elements.add(copy); selectedId = copy.id; _changed(); }
  void setBackground(Color color) { _checkpoint(); page.background = color; _changed(); }
  void resizeCanvas(double width, double height) { if (width < 64 || height < 64) return; _checkpoint(); final old = page.size; final sx = width / old.width, sy = height / old.height; page.size = CanvasSize(width, height); for (final e in elements) { e.x *= sx; e.y *= sy; e.width *= sx; e.height *= sy; } _changed(); }
  void addPage() { _checkpoint(); project.pages.add(DesignPage(title: 'Page ${project.pages.length + 1}', size: page.size)); currentPageIndex = project.pages.length - 1; selectedId = null; _changed(); }
  void duplicatePage() { _checkpoint(); final copy = page.clone()..title = '${page.title} Copy'; project.pages.insert(currentPageIndex + 1, copy); currentPageIndex++; selectedId = null; _changed(); }
  void deletePage() { if (project.pages.length <= 1) return; _checkpoint(); project.pages.removeAt(currentPageIndex); currentPageIndex = currentPageIndex.clamp(0, project.pages.length - 1); selectedId = null; _changed(); }
  void switchPage(int index) { if (index < 0 || index >= project.pages.length) return; currentPageIndex = index; selectedId = null; notifyListeners(); }
}
