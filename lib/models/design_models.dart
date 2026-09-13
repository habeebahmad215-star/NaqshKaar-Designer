import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';

const int kSchemaVersion = 2;

enum ElementKind { text, shape, image }

class CanvasSize {
  final double width;
  final double height;

  const CanvasSize(this.width, this.height);

  double get aspectRatio => height == 0 ? 1 : width / height;

  Map<String, dynamic> toJson() => {
        'width': width,
        'height': height,
      };

  factory CanvasSize.fromJson(Map<String, dynamic>? json) {
    final w = (json?['width'] as num?)?.toDouble() ?? 1080;
    final h = (json?['height'] as num?)?.toDouble() ?? 1080;

    return CanvasSize(
      w.clamp(64, 16000),
      h.clamp(64, 16000),
    );
  }
}

class DesignElement {
  String id;
  ElementKind kind;

  double x;
  double y;
  double width;
  double height;
  double rotation;
  double scaleX;
  double scaleY;
  double opacity;

  bool locked;
  bool hidden;

  int colorValue;

  String text;
  String fontFamily;
  double fontSize;
  bool bold;
  bool italic;

  TextAlign textAlign;
  TextDirection textDirection;

  Uint8List? imageBytes;

  double radius;

  DesignElement({
    required this.id,
    required this.kind,
    this.x = 0,
    this.y = 0,
    this.width = 200,
    this.height = 100,
    this.rotation = 0,
    this.scaleX = 1,
    this.scaleY = 1,
    this.opacity = 1,
    this.locked = false,
    this.hidden = false,
    this.colorValue = 0xFFD4AF37,
    this.text = '',
    this.fontFamily = 'JameelNoori',
    this.fontSize = 56,
    this.bold = false,
    this.italic = false,
    this.textAlign = TextAlign.center,
    this.textDirection = TextDirection.rtl,
    this.imageBytes,
    this.radius = 18,
  });

  Color get color => Color(colorValue);

  DesignElement clone() => DesignElement.fromJson(toJson());

  Map<String, dynamic> toJson() => {
        'id': id,
        'kind': kind.name,
        'x': x,
        'y': y,
        'width': width,
        'height': height,
        'rotation': rotation,
        'scaleX': scaleX,
        'scaleY': scaleY,
        'opacity': opacity,
        'locked': locked,
        'hidden': hidden,
        'color': colorValue,
        'text': text,
        'fontFamily': fontFamily,
        'fontSize': fontSize,
        'bold': bold,
        'italic': italic,
        'textAlign': textAlign.index,
        'textDirection':
            textDirection == TextDirection.rtl ? 'rtl' : 'ltr',
        'imageBytes':
            imageBytes == null ? null : base64Encode(imageBytes!),
        'radius': radius,
      };

  factory DesignElement.fromJson(Map<String, dynamic> json) {
    final kindName = json['kind']?.toString();

    final kind = ElementKind.values
            .where((e) => e.name == kindName)
            .firstOrNull ??
        ElementKind.text;

    final alignIndex =
        (json['textAlign'] as num?)?.toInt() ?? TextAlign.center.index;

    final align = alignIndex >= 0 &&
            alignIndex < TextAlign.values.length
        ? TextAlign.values[alignIndex]
        : TextAlign.center;

    Uint8List? bytes;

    final raw = json['imageBytes'];

    if (raw is String && raw.isNotEmpty) {
      try {
        bytes = base64Decode(raw);
      } catch (_) {}
    }

    return DesignElement(
      id: json['id']?.toString() ?? '',
      kind: kind,
      x: (json['x'] as num?)?.toDouble() ?? 0,
      y: (json['y'] as num?)?.toDouble() ?? 0,
      width: (json['width'] as num?)?.toDouble() ?? 200,
      height: (json['height'] as num?)?.toDouble() ?? 100,
      rotation: (json['rotation'] as num?)?.toDouble() ?? 0,
      scaleX: (json['scaleX'] as num?)?.toDouble() ?? 1,
      scaleY: (json['scaleY'] as num?)?.toDouble() ?? 1,
      opacity:
          ((json['opacity'] as num?)?.toDouble() ?? 1).clamp(0, 1),
      locked: json['locked'] as bool? ?? false,
      hidden: json['hidden'] as bool? ?? false,
      colorValue:
          (json['color'] as num?)?.toInt() ?? 0xFFD4AF37,
      text: json['text']?.toString() ?? '',
      fontFamily:
          json['fontFamily']?.toString() ?? 'JameelNoori',
      fontSize:
          (json['fontSize'] as num?)?.toDouble() ?? 56,
      bold: json['bold'] as bool? ?? false,
      italic: json['italic'] as bool? ?? false,
      textAlign: align,
      textDirection:
          json['textDirection'] == 'ltr'
              ? TextDirection.ltr
              : TextDirection.rtl,
      imageBytes: bytes,
      radius:
          (json['radius'] as num?)?.toDouble() ?? 18,
    );
  }
}

class DesignPage {
  String title;
  CanvasSize size;
  Color background;
  List<DesignElement> elements;

  DesignPage({
    required this.title,
    required this.size,
    this.background = Colors.white,
    List<DesignElement>? elements,
  }) : elements = elements ?? [];

  DesignPage clone() => DesignPage.fromJson(toJson());

  Map<String, dynamic> toJson() => {
        'title': title,
        'size': size.toJson(),
        'background': background.value,
        'elements':
            elements.map((e) => e.toJson()).toList(),
      };

  factory DesignPage.fromJson(Map<String, dynamic> json) =>
      DesignPage(
        title: json['title']?.toString() ?? 'Page',
        size: CanvasSize.fromJson(
          json['size'] as Map<String, dynamic>?,
        ),
        background: Color(
          (json['background'] as num?)?.toInt() ??
              Colors.white.value,
        ),
        elements: (json['elements'] is List)
            ? (json['elements'] as List)
                .whereType<Map>()
                .map(
                  (e) => DesignElement.fromJson(
                    Map<String, dynamic>.from(e),
                  ),
                )
                .toList()
            : [],
      );
}

class ProjectModel {
  String id;
  String name;
  int lastModified;
  List<DesignPage> pages;

  ProjectModel({
    required this.id,
    required this.name,
    required this.pages,
    int? lastModified,
  }) : lastModified =
            lastModified ?? DateTime.now().millisecondsSinceEpoch;

  Map<String, dynamic> toJson() => {
        'schemaVersion': kSchemaVersion,
        'id': id,
        'name': name,
        'lastModified': lastModified,
        'pages':
            pages.map((p) => p.toJson()).toList(),
      };

  factory ProjectModel.fromJson(Map<String, dynamic> json) =>
      ProjectModel(
        id: json['id']?.toString() ?? '',
        name: json['name']?.toString() ?? 'Project',
        lastModified:
            (json['lastModified'] as num?)?.toInt(),
        pages: (json['pages'] is List)
            ? (json['pages'] as List)
                .whereType<Map>()
                .map(
                  (p) => DesignPage.fromJson(
                    Map<String, dynamic>.from(p),
                  ),
                )
                .toList()
            : [],
      );
}

extension FirstOrNullExtension<T> on Iterable<T> {
  T? get firstOrNull => isEmpty ? null : first;
}
