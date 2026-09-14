import 'dart:math' as math;
import 'package:flutter/material.dart';
import '../models/design_models.dart';
import '../state/workspace_controller.dart';

class DesignCanvas extends StatefulWidget {
  final WorkspaceController controller;
  final GlobalKey repaintKey;

  const DesignCanvas({
    super.key,
    required this.controller,
    required this.repaintKey,
  });

  @override
  State<DesignCanvas> createState() => _DesignCanvasState();
}

class _DesignCanvasState extends State<DesignCanvas> {
  double? _rotationStartAngle;
  double? _rotationStartValue;

  WorkspaceController get controller => widget.controller;

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
            decoration: BoxDecoration(color: page.background),
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
        child = Text(
          e.text.isEmpty ? 'Text' : e.text,
          textAlign: e.textAlign,
          textDirection: e.textDirection,
          style: TextStyle(
            fontFamily: e.fontFamily,
            fontSize: e.fontSize,
            color: e.color,
            fontWeight: e.bold ? FontWeight.bold : FontWeight.normal,
            fontStyle: e.italic ? FontStyle.italic : FontStyle.normal,
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
                        details.delta.dx,
                        details.delta.dy,
                      );
                    },
              onPanEnd: e.locked
                  ? null
                  : (_) => controller.finishContinuousEdit(),
              child: DecoratedBox(
                decoration: selected
                    ? BoxDecoration(
                        border: Border.all(
                          color: const Color(0xFF7C3AED),
                          width: 3,
                        ),
                      )
                    : const BoxDecoration(),
                child: Padding(
                  padding: const EdgeInsets.all(8),
                  child: child,
                ),
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
            details.delta.dx,
            details.delta.dy,
          );
        },
        onPanEnd: (_) => controller.finishContinuousEdit(),
        child: Container(
          width: 30,
          height: 30,
          alignment: Alignment.center,
          child: Container(
            width: 18,
            height: 18,
            decoration: BoxDecoration(
              color: Colors.white,
              border: Border.all(color: const Color(0xFF7C3AED), width: 3),
              borderRadius: BorderRadius.circular(5),
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
    );
  }

  Widget _rotationHandle(DesignElement e) {
    return Align(
      alignment: Alignment.topCenter,
      child: Transform.translate(
        offset: const Offset(0, -42),
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
            width: 34,
            height: 34,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: Colors.white,
              border: Border.all(color: const Color(0xFF7C3AED), width: 3),
              boxShadow: const [
                BoxShadow(
                  blurRadius: 5,
                  spreadRadius: 1,
                  color: Colors.black26,
                ),
              ],
            ),
            child: const Icon(
              Icons.rotate_right_rounded,
              size: 21,
              color: Color(0xFF7C3AED),
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
