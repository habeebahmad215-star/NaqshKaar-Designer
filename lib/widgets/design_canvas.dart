import 'dart:math' as math;
import 'package:flutter/material.dart';
import '../models/design_models.dart';
import '../state/workspace_controller.dart';

class DesignCanvas extends StatefulWidget {
  final WorkspaceController controller;
  final GlobalKey repaintKey;
  final double interactionScale;

  const DesignCanvas({
    super.key,
    required this.controller,
    required this.repaintKey,
    this.interactionScale = 1,
  });

  @override
  State<DesignCanvas> createState() => _DesignCanvasState();
}

class _DesignCanvasState extends State<DesignCanvas> {
  double? _rotationStartAngle;
  double? _rotationStartValue;

  WorkspaceController get controller => widget.controller;
  double get scale => widget.interactionScale.clamp(.05, 10);

  @override
  Widget build(BuildContext context) {
    final page = controller.page;

    return RepaintBoundary(
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
              boxShadow: const [
                BoxShadow(
                  blurRadius: 22,
                  spreadRadius: 1,
                  offset: Offset(0, 8),
                  color: Color(0x26000000),
                ),
              ],
            ),
            child: Stack(
              clipBehavior: Clip.none,
              children: [for (final e in page.elements) _element(e)],
            ),
          ),
        ),
      ),
    );
  }

  Widget _element(DesignElement e) {
    if (e.hidden) return const SizedBox.shrink();

    final selected = controller.selectedId == e.id;
    Widget child;

    switch (e.kind) {
      case ElementKind.text:
        child = Center(
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
              height: 1.25,
            ),
          ),
        );
        break;
      case ElementKind.shape:
        child = DecoratedBox(
          decoration: BoxDecoration(
            color: e.color,
            borderRadius: BorderRadius.circular(e.radius),
          ),
        );
        break;
      case ElementKind.image:
        child = e.imageBytes == null
            ? const ColoredBox(color: Colors.black12)
            : Image.memory(e.imageBytes!, fit: BoxFit.cover);
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
              onPanStart: e.locked
                  ? null
                  : (_) {
                      controller.select(e.id);
                      controller.startContinuousEdit();
                    },
              onPanUpdate: e.locked
                  ? null
                  : (details) {
                      controller.moveSelectedBy(
                        details.delta.dx / scale,
                        details.delta.dy / scale,
                      );
                    },
              onPanEnd: e.locked
                  ? null
                  : (_) => controller.finishContinuousEdit(),
              child: DecoratedBox(
                decoration: selected
                    ? BoxDecoration(
                        border: Border.all(
                          color: const Color(0xFF6D28D9),
                          width: 2 / scale,
                        ),
                      )
                    : const BoxDecoration(),
                child: child,
              ),
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
            _handle(e, 'top-left', Alignment.topLeft),
            _handle(e, 'top-right', Alignment.topRight),
            _handle(e, 'bottom-left', Alignment.bottomLeft),
            _handle(e, 'bottom-right', Alignment.bottomRight),
            _rotationHandle(e),
          ],
        ),
      ),
    );
  }

  Widget _handle(DesignElement e, String type, Alignment alignment) {
    final touchSize = 34 / scale;
    final visualSize = 18 / scale;
    return Align(
      alignment: alignment,
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onPanStart: (_) {
          controller.select(e.id);
          controller.startContinuousEdit();
        },
        onPanUpdate: (details) {
          controller.resizeSelectedFromHandle(
            type,
            details.delta.dx / scale,
            details.delta.dy / scale,
          );
        },
        onPanEnd: (_) => controller.finishContinuousEdit(),
        child: SizedBox(
          width: touchSize,
          height: touchSize,
          child: Center(
            child: Container(
              width: visualSize,
              height: visualSize,
              decoration: BoxDecoration(
                color: Colors.white,
                border: Border.all(color: const Color(0xFF6D28D9), width: 2 / scale),
                borderRadius: BorderRadius.circular(4 / scale),
                boxShadow: const [
                  BoxShadow(
                    blurRadius: 5,
                    spreadRadius: 1,
                    color: Colors.black26,
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _rotationHandle(DesignElement e) {
    final size = 34 / scale;
    return Align(
      alignment: Alignment.topCenter,
      child: Transform.translate(
        offset: Offset(0, -42 / scale),
        child: GestureDetector(
          behavior: HitTestBehavior.opaque,
          onPanStart: (details) {
            controller.select(e.id);
            controller.startContinuousEdit();
            final center = _globalCenter(e);
            _rotationStartAngle = math.atan2(
              details.globalPosition.dy - center.dy,
              details.globalPosition.dx - center.dx,
            );
            _rotationStartValue = e.rotation;
          },
          onPanUpdate: (details) {
            final startAngle = _rotationStartAngle;
            final startValue = _rotationStartValue;
            if (startAngle == null || startValue == null) return;
            final center = _globalCenter(e);
            final currentAngle = math.atan2(
              details.globalPosition.dy - center.dy,
              details.globalPosition.dx - center.dx,
            );
            var delta = currentAngle - startAngle;
            if (delta > math.pi) delta -= math.pi * 2;
            if (delta < -math.pi) delta += math.pi * 2;
            controller.rotateSelectedTo(startValue + delta);
          },
          onPanEnd: (_) {
            _rotationStartAngle = null;
            _rotationStartValue = null;
            controller.finishContinuousEdit();
          },
          child: Container(
            width: size,
            height: size,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: Colors.white,
              border: Border.all(color: const Color(0xFF6D28D9), width: 2 / scale),
              boxShadow: const [
                BoxShadow(
                  blurRadius: 5,
                  spreadRadius: 1,
                  color: Colors.black26,
                ),
              ],
            ),
            child: Icon(
              Icons.rotate_right_rounded,
              size: 20 / scale,
              color: const Color(0xFF6D28D9),
            ),
          ),
        ),
      ),
    );
  }

  Offset _globalCenter(DesignElement e) {
    final box = widget.repaintKey.currentContext?.findRenderObject();
    if (box is RenderBox) {
      return box.localToGlobal(
        Offset(e.x + e.width / 2, e.y + e.height / 2),
      );
    }
    return Offset(e.x + e.width / 2, e.y + e.height / 2);
  }
}
