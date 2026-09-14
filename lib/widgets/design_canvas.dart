import 'dart:math' as math;
import 'package:flutter/material.dart';
import '../models/design_models.dart';
import '../state/workspace_controller.dart';
import 'layers_panel.dart';

class DesignCanvas extends StatefulWidget {
  final WorkspaceController controller;
  final GlobalKey repaintKey;
  final double interactionScale;
  const DesignCanvas({super.key, required this.controller, required this.repaintKey, this.interactionScale = 1});
  @override State<DesignCanvas> createState() => _DesignCanvasState();
}

class _DesignCanvasState extends State<DesignCanvas> {
  double? _rotationStartAngle, _rotationStartValue;
  WorkspaceController get controller => widget.controller;
  double get scale => widget.interactionScale.clamp(.05, 10);
  @override
  Widget build(BuildContext context) {
    final page = controller.page;
    return Stack(
      clipBehavior: Clip.none,
      children: [
        RepaintBoundary(key: widget.repaintKey, child: SizedBox(width: page.size.width, height: page.size.height, child: GestureDetector(
          behavior: HitTestBehavior.opaque, onTap: () => controller.select(null),
          child: DecoratedBox(decoration: BoxDecoration(color: page.background, boxShadow: const [BoxShadow(blurRadius: 22, spreadRadius: 1, offset: Offset(0, 8), color: Color(0x26000000))]), child: Stack(clipBehavior: Clip.none, children: [for (final e in page.elements) _element(e)])),
        ))),
        Positioned(
          top: -8,
          right: -8,
          child: Material(
            color: Colors.white,
            elevation: 4,
            borderRadius: BorderRadius.circular(14),
            child: IconButton(
              tooltip: 'Layers',
              onPressed: _layersSheet,
              icon: const Icon(Icons.layers_rounded, color: Color(0xFF6D28D9)),
            ),
          ),
        ),
      ],
    );
  }
  Future<void> _layersSheet() async {
    await showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      showDragHandle: true,
      builder: (_) => SizedBox(
        height: MediaQuery.sizeOf(context).height * .72,
        child: LayersPanel(controller: controller),
      ),
    );
  }
  List<BoxShadow> _shadows(DesignElement e) => e.shadowBlur <= 0 || e.shadowColor.a <= 0 ? const [] : [BoxShadow(color: e.shadowColor, blurRadius: e.shadowBlur, offset: Offset(e.shadowOffsetX, e.shadowOffsetY))];
  BoxDecoration _decoration(DesignElement e, {required bool selected, required bool isShape}) => BoxDecoration(
    color: isShape ? e.color : null, borderRadius: isShape ? BorderRadius.circular(e.radius) : null,
    border: e.strokeWidth > 0 && e.strokeColor.a > 0 ? Border.all(color: e.strokeColor, width: e.strokeWidth) : selected ? Border.all(color: const Color(0xFF6D28D9), width: 2 / scale) : null,
    boxShadow: _shadows(e));
  Widget _element(DesignElement e) {
    if (e.hidden) return const SizedBox.shrink();
    final selected = controller.selectedId == e.id;
    Widget child;
    switch (e.kind) {
      case ElementKind.text:
        child = Container(decoration: _decoration(e, selected: selected, isShape: false), alignment: Alignment.center, child: Text(
          e.text.isEmpty ? 'Text' : e.text, textAlign: e.textAlign, textDirection: e.textDirection,
          style: TextStyle(fontFamily: e.fontFamily == 'JameelNoori' ? 'Gulzar' : e.fontFamily, fontSize: e.fontSize, color: e.color, fontWeight: e.bold ? FontWeight.bold : FontWeight.normal, fontStyle: e.italic ? FontStyle.italic : FontStyle.normal, height: e.lineHeight, letterSpacing: e.letterSpacing,
            shadows: _shadows(e).map((s) => Shadow(color: s.color, blurRadius: s.blurRadius, offset: s.offset)).toList()),
        ));
        break;
      case ElementKind.shape:
        child = DecoratedBox(decoration: _decoration(e, selected: selected, isShape: true));
        break;
      case ElementKind.image:
        child = Container(decoration: _decoration(e, selected: selected, isShape: false), clipBehavior: Clip.antiAlias, child: e.imageBytes == null ? const ColoredBox(color: Colors.black12) : Image.memory(e.imageBytes!, fit: BoxFit.cover));
        break;
    }
    child = Opacity(opacity: e.opacity, child: child);
    return Positioned(left: e.x, top: e.y, width: e.width, height: e.height, child: Transform.rotate(angle: e.rotation, alignment: Alignment.center, child: Stack(clipBehavior: Clip.none, children: [
      GestureDetector(behavior: HitTestBehavior.opaque, onTap: () => controller.select(e.id), onPanStart: e.locked ? null : (_) { controller.select(e.id); controller.startContinuousEdit(); }, onPanUpdate: e.locked ? null : (d) => controller.moveSelectedBy(d.delta.dx / scale, d.delta.dy / scale), onPanEnd: e.locked ? null : (_) => controller.finishContinuousEdit(), child: child),
      if (selected && !e.locked) _selectionHandles(e),
    ])));
  }
  Widget _selectionHandles(DesignElement e) => Positioned.fill(child: IgnorePointer(ignoring: false, child: Stack(clipBehavior: Clip.none, children: [_handle(e, 'top-left', Alignment.topLeft), _handle(e, 'top-right', Alignment.topRight), _handle(e, 'bottom-left', Alignment.bottomLeft), _handle(e, 'bottom-right', Alignment.bottomRight), _rotationHandle(e)])));
  Widget _handle(DesignElement e, String type, Alignment alignment) {
    final touchSize = 34 / scale, visualSize = 18 / scale;
    return Align(alignment: alignment, child: GestureDetector(behavior: HitTestBehavior.opaque, onPanStart: (_) { controller.select(e.id); controller.startContinuousEdit(); }, onPanUpdate: (d) => controller.resizeSelectedFromHandle(type, d.delta.dx / scale, d.delta.dy / scale), onPanEnd: (_) => controller.finishContinuousEdit(), child: SizedBox(width: touchSize, height: touchSize, child: Center(child: Container(width: visualSize, height: visualSize, decoration: BoxDecoration(color: Colors.white, border: Border.all(color: const Color(0xFF6D28D9), width: 2 / scale), borderRadius: BorderRadius.circular(4 / scale), boxShadow: const [BoxShadow(blurRadius: 5, spreadRadius: 1, color: Colors.black26)]))))));
  }
  Widget _rotationHandle(DesignElement e) {
    final size = 34 / scale;
    return Align(alignment: Alignment.topCenter, child: Transform.translate(offset: Offset(0, -42 / scale), child: GestureDetector(behavior: HitTestBehavior.opaque,
      onPanStart: (d) { controller.select(e.id); controller.startContinuousEdit(); final center = _globalCenter(e); _rotationStartAngle = math.atan2(d.globalPosition.dy - center.dy, d.globalPosition.dx - center.dx); _rotationStartValue = e.rotation; },
      onPanUpdate: (d) { final a = _rotationStartAngle, v = _rotationStartValue; if (a == null || v == null) return; final center = _globalCenter(e); final current = math.atan2(d.globalPosition.dy - center.dy, d.globalPosition.dx - center.dx); var delta = current - a; if (delta > math.pi) delta -= math.pi * 2; if (delta < -math.pi) delta += math.pi * 2; controller.rotateSelectedTo(v + delta); },
      onPanEnd: (_) { _rotationStartAngle = null; _rotationStartValue = null; controller.finishContinuousEdit(); }, child: Container(width: size, height: size, decoration: BoxDecoration(shape: BoxShape.circle, color: Colors.white, border: Border.all(color: const Color(0xFF6D28D9), width: 2 / scale), boxShadow: const [BoxShadow(blurRadius: 5, spreadRadius: 1, color: Colors.black26)]), child: Icon(Icons.rotate_right_rounded, size: 20 / scale, color: const Color(0xFF6D28D9))),
    )));
  }
  Offset _globalCenter(DesignElement e) { final box = widget.repaintKey.currentContext?.findRenderObject(); if (box is RenderBox) return box.localToGlobal(Offset(e.x + e.width / 2, e.y + e.height / 2)); return Offset(e.x + e.width / 2, e.y + e.height / 2); }
}
