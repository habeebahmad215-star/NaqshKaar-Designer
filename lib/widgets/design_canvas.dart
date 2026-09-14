import 'package:flutter/material.dart';
import '../models/design_models.dart';
import '../state/workspace_controller.dart';

class DesignCanvas extends StatelessWidget {
  final WorkspaceController controller;
  final GlobalKey repaintKey;

  const DesignCanvas({
    super.key,
    required this.controller,
    required this.repaintKey,
  });

  @override
  Widget build(BuildContext context) {
    final page = controller.page;

    return RepaintBoundary(
      key: repaintKey,
      child: SizedBox(
        width: page.size.width,
        height: page.size.height,
        child: GestureDetector(
          behavior: HitTestBehavior.opaque,
          onTap: () => controller.select(null),
          child: DecoratedBox(
            decoration: BoxDecoration(color: page.background),
            child: Stack(
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
        child: GestureDetector(
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
      ),
    );
  }
}
