import 'dart:math' as math;
import 'package:flutter/material.dart';
import '../models/design_models.dart';
import '../state/workspace_controller.dart';
import 'layers_panel.dart';

/// High quality mobile transform overlay.
///
/// The selection UI is deliberately independent from the object's decoration:
/// handles stay visually inside the page, remain easy to touch at any zoom,
/// and transform in the object's local coordinate space.
class DesignCanvas extends StatefulWidget {
  final WorkspaceController controller;
  final GlobalKey repaintKey;
  final double interactionScale;
  const DesignCanvas({super.key, required this.controller, required this.repaintKey, this.interactionScale = 1});
  @override State<DesignCanvas> createState() => _DesignCanvasState();
}

class _DesignCanvasState extends State<DesignCanvas> {
  double? _rotationStartAngle;
  double? _rotationStartValue;
  WorkspaceController get controller => widget.controller;
  double get scale => widget.interactionScale.clamp(.05, 10);
  static const _purple = Color(0xFF6D28D9);
  static const _touch = 44.0;
  static const _visual = 16.0;

  @override
  Widget build(BuildContext context) {
    final page = controller.page;
    return Stack(
      clipBehavior: Clip.hardEdge,
      children: [
        RepaintBoundary(
          key: widget.repaintKey,
          child: SizedBox(
            width: page.size.width,
            height: page.size.height,
            child: GestureDetector(
              behavior: HitTestBehavior.opaque,
              onTap: () => controller.select(null),
              child: DecoratedBox(
                decoration: BoxDecoration(
                  color: page.background,
                  boxShadow: const [BoxShadow(blurRadius: 22, spreadRadius: 1, offset: Offset(0, 8), color: Color(0x26000000))],
                ),
                child: Stack(
                  clipBehavior: Clip.hardEdge,
                  children: [for (final e in page.elements) _element(e)],
                ),
              ),
            ),
          ),
        ),
        Positioned(
          top: 8,
          right: 8,
          child: Material(
            color: Colors.white,
            elevation: 4,
            borderRadius: BorderRadius.circular(14),
            child: IconButton(
              tooltip: 'Layers',
              onPressed: _layersSheet,
              icon: const Icon(Icons.layers_rounded, color: _purple),
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
      builder: (_) => SizedBox(height: MediaQuery.sizeOf(context).height * .72, child: LayersPanel(controller: controller)),
    );
  }

  List<BoxShadow> _shadows(DesignElement e) => e.shadowBlur <= 0 || e.shadowColor.a <= 0
      ? const []
      : [BoxShadow(color: e.shadowColor, blurRadius: e.shadowBlur, offset: Offset(e.shadowOffsetX, e.shadowOffsetY))];

  BoxDecoration _decoration(DesignElement e, {required bool selected, required bool isShape}) => BoxDecoration(
    color: isShape ? e.color : null,
    borderRadius: isShape ? BorderRadius.circular(e.radius) : null,
    border: e.strokeWidth > 0 && e.strokeColor.a > 0
        ? Border.all(color: e.strokeColor, width: e.strokeWidth)
        : null,
    boxShadow: _shadows(e),
  );

  Widget _element(DesignElement e) {
    if (e.hidden) return const SizedBox.shrink();
    final selected = controller.selectedId == e.id;
    Widget child;
    switch (e.kind) {
      case ElementKind.text:
        child = Container(
          decoration: _decoration(e, selected: selected, isShape: false),
          alignment: Alignment.center,
          child: Text(
            e.text.isEmpty ? 'Text' : e.text,
            textAlign: e.textAlign,
            textDirection: e.textDirection,
            style: TextStyle(
              fontFamily: e.fontFamily == 'JameelNoori' ? 'Gulzar' : e.fontFamily,
              fontSize: e.fontSize,
              color: e.color,
              fontWeight: e.bold ? FontWeight.bold : FontWeight.normal,
              fontStyle: e.italic ? FontStyle.italic : FontStyle.normal,
              height: e.lineHeight,
              letterSpacing: e.letterSpacing,
              shadows: _shadows(e).map((s) => Shadow(color: s.color, blurRadius: s.blurRadius, offset: s.offset)).toList(),
            ),
          ),
        );
        break;
      case ElementKind.shape:
        child = DecoratedBox(decoration: _decoration(e, selected: selected, isShape: true));
        break;
      case ElementKind.image:
        child = Container(
          decoration: _decoration(e, selected: selected, isShape: false),
          clipBehavior: Clip.antiAlias,
          child: e.imageBytes == null ? const ColoredBox(color: Colors.black12) : Image.memory(e.imageBytes!, fit: BoxFit.cover),
        );
        break;
    }
    child = Opacity(opacity: e.opacity, child: child);
    return Positioned(
      left: e.x,
      top: e.y,
      width: e.width,
      height: e.height,
      child: Transform.rotate(
        angle: e.rotation,
        alignment: Alignment.center,
        child: Stack(
          clipBehavior: Clip.hardEdge,
          children: [
            GestureDetector(
              behavior: HitTestBehavior.opaque,
              onTap: () => controller.select(e.id),
              onPanStart: e.locked ? null : (_) {
                controller.select(e.id);
                controller.startContinuousEdit();
              },
              onPanUpdate: e.locked ? null : (d) => controller.moveSelectedBy(d.delta.dx / scale, d.delta.dy / scale),
              onPanEnd: e.locked ? null : (_) => controller.finishContinuousEdit(),
              child: child,
            ),
            if (selected && !e.locked) _selectionHandles(e),
          ],
        ),
      ),
    );
  }

  Widget _selectionHandles(DesignElement e) {
    // Every visual handle is kept inside the object's box. The larger gesture
    // targets make the controls comfortable on phones without leaking outside.
    return Positioned.fill(
      child: Stack(
        clipBehavior: Clip.hardEdge,
        children: [
          _cornerHandle(e, 'top-left', 0, 0, Alignment.topLeft),
          _cornerHandle(e, 'top-right', 1, 0, Alignment.topRight),
          _cornerHandle(e, 'bottom-left', 0, 1, Alignment.bottomLeft),
          _cornerHandle(e, 'bottom-right', 1, 1, Alignment.bottomRight),
          _edgeHandle(e, 'top', Alignment.topCenter),
          _edgeHandle(e, 'bottom', Alignment.bottomCenter),
          _edgeHandle(e, 'left', Alignment.centerLeft),
          _edgeHandle(e, 'right', Alignment.centerRight),
          _rotationHandle(e),
        ],
      ),
    );
  }

  Widget _cornerHandle(DesignElement e, String type, double x, double y, Alignment alignment) {
    final touch = _touch / scale;
    final visual = _visual / scale;
    final dx = x == 0 ? touch / 2 : -touch / 2;
    final dy = y == 0 ? touch / 2 : -touch / 2;
    return Align(
      alignment: alignment,
      child: Transform.translate(
        offset: Offset(dx, dy),
        child: GestureDetector(
          behavior: HitTestBehavior.opaque,
          onPanStart: (_) { controller.select(e.id); controller.startContinuousEdit(); },
          onPanUpdate: (d) => controller.resizeSelectedFromHandle(type, d.delta.dx / scale, d.delta.dy / scale),
          onPanEnd: (_) => controller.finishContinuousEdit(),
          child: SizedBox(
            width: touch,
            height: touch,
            child: Center(child: _handleVisual(visual, Icons.circle)),
          ),
        ),
      ),
    );
  }

  Widget _edgeHandle(DesignElement e, String type, Alignment alignment) {
    final touch = _touch / scale;
    final visual = 6.0 / scale;
    return Align(
      alignment: alignment,
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onPanStart: (_) { controller.select(e.id); controller.startContinuousEdit(); },
        onPanUpdate: (d) => controller.resizeSelectedFromHandle(type, d.delta.dx / scale, d.delta.dy / scale),
        onPanEnd: (_) => controller.finishContinuousEdit(),
        child: SizedBox(
          width: alignment == Alignment.centerLeft || alignment == Alignment.centerRight ? touch : math.max(touch, e.width),
          height: alignment == Alignment.topCenter || alignment == Alignment.bottomCenter ? touch : math.max(touch, e.height),
          child: Center(child: Container(width: visual, height: visual, decoration: BoxDecoration(color: Colors.white, border: Border.all(color: _purple, width: 2 / scale), borderRadius: BorderRadius.circular(3 / scale)))),
        ),
      ),
    );
  }

  Widget _handleVisual(double size, IconData icon) => Container(
    width: size,
    height: size,
    decoration: BoxDecoration(
      color: Colors.white,
      shape: BoxShape.circle,
      border: Border.all(color: _purple, width: 2 / scale),
      boxShadow: const [BoxShadow(blurRadius: 4, spreadRadius: .5, color: Colors.black26)],
    ),
  );

  Widget _rotationHandle(DesignElement e) {
    final touch = _touch / scale;
    final visual = 18.0 / scale;
    return Positioned(
      top: 2 / scale,
      left: (e.width - touch) / 2,
      width: touch,
      height: touch,
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onPanStart: (d) {
          controller.select(e.id);
          controller.startContinuousEdit();
          final center = _globalCenter(e);
          _rotationStartAngle = math.atan2(d.globalPosition.dy - center.dy, d.globalPosition.dx - center.dx);
          _rotationStartValue = e.rotation;
        },
        onPanUpdate: (d) {
          final a = _rotationStartAngle, v = _rotationStartValue;
          if (a == null || v == null) return;
          final center = _globalCenter(e);
          final current = math.atan2(d.globalPosition.dy - center.dy, d.globalPosition.dx - center.dx);
          var delta = current - a;
          if (delta > math.pi) delta -= math.pi * 2;
          if (delta < -math.pi) delta += math.pi * 2;
          controller.rotateSelectedTo(v + delta);
        },
        onPanEnd: (_) {
          _rotationStartAngle = null;
          _rotationStartValue = null;
          controller.finishContinuousEdit();
        },
        child: Center(
          child: Container(
            width: visual,
            height: visual,
            decoration: BoxDecoration(color: Colors.white, shape: BoxShape.circle, border: Border.all(color: _purple, width: 2 / scale), boxShadow: const [BoxShadow(blurRadius: 5, spreadRadius: 1, color: Colors.black26)]),
            child: Icon(Icons.rotate_right_rounded, size: 12 / scale, color: _purple),
          ),
        ),
      ),
    );
  }

  Offset _globalCenter(DesignElement e) {
    final box = widget.repaintKey.currentContext?.findRenderObject();
    if (box is RenderBox) return box.localToGlobal(Offset(e.x + e.width / 2, e.y + e.height / 2));
    return Offset(e.x + e.width / 2, e.y + e.height / 2);
  }
}
