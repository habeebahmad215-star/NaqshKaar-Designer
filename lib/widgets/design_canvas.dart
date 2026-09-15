import 'dart:math' as math;
import 'package:flutter/material.dart';
import '../models/design_models.dart';
import '../state/workspace_controller.dart';
import 'layers_panel.dart';

/// Clean, Canva-style selection overlay for mobile editing.
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
  static const _handleWhite = Colors.white;
  static const _touch = 44.0;
  static const _cornerVisual = 12.0;
  static const _edgeVisual = 8.0;

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

  BoxDecoration _decoration(DesignElement e, {required bool isShape}) => BoxDecoration(
    color: isShape ? e.color : null,
    borderRadius: isShape ? BorderRadius.circular(e.radius) : null,
    border: e.strokeWidth > 0 && e.strokeColor.a > 0 ? Border.all(color: e.strokeColor, width: e.strokeWidth) : null,
    boxShadow: _shadows(e),
  );

  Widget _element(DesignElement e) {
    if (e.hidden) return const SizedBox.shrink();
    final selected = controller.selectedId == e.id;
    Widget child;
    switch (e.kind) {
      case ElementKind.text:
        child = Container(
          decoration: _decoration(e, isShape: false),
          alignment: Alignment.center,
          child: FittedBox(
            fit: BoxFit.scaleDown,
            alignment: Alignment.center,
            child: SizedBox(
              width: e.width,
              child: Text(
                e.text.isEmpty ? 'Text' : e.text,
                textAlign: e.textAlign,
                textDirection: e.textDirection,
                style: TextStyle(
                  fontFamily: e.fontFamily,
                  fontSize: e.fontSize,
                  color: e.color,
                  fontWeight: e.bold ? FontWeight.bold : FontWeight.normal,
                  fontStyle: e.italic ? FontStyle.italic : FontStyle.normal,
                  height: e.lineHeight,
                  letterSpacing: e.letterSpacing,
                  shadows: _shadows(e).map((s) => Shadow(color: s.color, blurRadius: s.blurRadius, offset: s.offset)).toList(),
                ),
              ),
            ),
          ),
        );
        break;
      case ElementKind.shape:
        child = DecoratedBox(decoration: _decoration(e, isShape: true));
        break;
      case ElementKind.image:
        child = Container(
          decoration: _decoration(e, isShape: false),
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
          clipBehavior: Clip.none,
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
    return Positioned.fill(
      child: IgnorePointer(
        ignoring: false,
        child: Stack(
          clipBehavior: Clip.none,
          children: [
            Positioned.fill(child: IgnorePointer(child: CustomPaint(painter: _SelectionBorderPainter(color: _purple, strokeWidth: 1.5 / scale)))),
            _cornerHandle(e, 'top-left', Alignment.topLeft),
            _cornerHandle(e, 'top-right', Alignment.topRight),
            _cornerHandle(e, 'bottom-left', Alignment.bottomLeft),
            _cornerHandle(e, 'bottom-right', Alignment.bottomRight),
            _edgeHandle(e, 'top', Alignment.topCenter),
            _edgeHandle(e, 'bottom', Alignment.bottomCenter),
            _edgeHandle(e, 'left', Alignment.centerLeft),
            _edgeHandle(e, 'right', Alignment.centerRight),
            _rotationHandle(e),
          ],
        ),
      ),
    );
  }

  Widget _cornerHandle(DesignElement e, String type, Alignment alignment) {
    final touch = _touch / scale;
    final visual = _cornerVisual / scale;
    return Align(
      alignment: alignment,
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onPanStart: (_) { controller.select(e.id); controller.startContinuousEdit(); },
        onPanUpdate: (d) => controller.resizeSelectedFromHandle(type, d.delta.dx / scale, d.delta.dy / scale),
        onPanEnd: (_) => controller.finishContinuousEdit(),
        child: SizedBox(
          width: touch,
          height: touch,
          child: Center(
            child: Container(
              width: visual,
              height: visual,
              decoration: BoxDecoration(
                color: _handleWhite,
                shape: BoxShape.circle,
                border: Border.all(color: _purple, width: 2 / scale),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _edgeHandle(DesignElement e, String type, Alignment alignment) {
    final touch = _touch / scale;
    final visual = _edgeVisual / scale;
    final horizontal = alignment == Alignment.topCenter || alignment == Alignment.bottomCenter;
    return Align(
      alignment: alignment,
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onPanStart: (_) { controller.select(e.id); controller.startContinuousEdit(); },
        onPanUpdate: (d) => controller.resizeSelectedFromHandle(type, d.delta.dx / scale, d.delta.dy / scale),
        onPanEnd: (_) => controller.finishContinuousEdit(),
        child: SizedBox(
          width: horizontal ? math.max(touch, math.min(e.width, 180.0)) : touch,
          height: horizontal ? touch : math.max(touch, math.min(e.height, 180.0)),
          child: Center(
            child: Container(
              width: horizontal ? 30 / scale : visual,
              height: horizontal ? visual : 30 / scale,
              decoration: BoxDecoration(
                color: _handleWhite,
                border: Border.all(color: _purple, width: 1.8 / scale),
                borderRadius: BorderRadius.circular(4 / scale),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _rotationHandle(DesignElement e) {
    final touch = _touch / scale;
    final visual = 18.0 / scale;
    final stemHeight = 18.0 / scale;
    return Positioned(
      top: -touch - stemHeight + 8 / scale,
      left: (e.width - touch) / 2,
      width: touch,
      height: touch + stemHeight,
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
        child: Column(
          children: [
            Container(
              width: visual,
              height: visual,
              decoration: BoxDecoration(
                color: _handleWhite,
                shape: BoxShape.circle,
                border: Border.all(color: _purple, width: 2 / scale),
              ),
              child: Icon(Icons.rotate_right_rounded, size: 11 / scale, color: _purple),
            ),
            Container(width: 1.5 / scale, height: stemHeight, color: _purple),
          ],
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

class _SelectionBorderPainter extends CustomPainter {
  final Color color;
  final double strokeWidth;
  const _SelectionBorderPainter({required this.color, required this.strokeWidth});
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth;
    canvas.drawRect(Rect.fromLTWH(strokeWidth / 2, strokeWidth / 2, size.width - strokeWidth, size.height - strokeWidth), paint);
  }
  @override
  bool shouldRepaint(covariant _SelectionBorderPainter old) => old.color != color || old.strokeWidth != strokeWidth;
}
