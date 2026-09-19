import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';

const int kSchemaVersion = 3;

enum ElementKind { text, shape, image }

class CanvasSize {
  final double width;
  final double height;
  const CanvasSize(this.width, this.height);
  double get aspectRatio => height == 0 ? 1 : width / height;
  Map<String, dynamic> toJson() => {'width': width, 'height': height};
  factory CanvasSize.fromJson(Map<String, dynamic>? json) => CanvasSize(
        ((json?['width'] as num?)?.toDouble() ?? 1080).clamp(64, 16000),
        ((json?['height'] as num?)?.toDouble() ?? 1080).clamp(64, 16000),
      );
}

class DesignElement {
  String id;
  ElementKind kind;
  double x, y, width, height, rotation, scaleX, scaleY, opacity;
  bool locked, hidden;
  int colorValue;
  int strokeColorValue;
  double strokeWidth;
  int shadowColorValue;
  double shadowBlur;
  double shadowOffsetX;
  double shadowOffsetY;
  String text;
  String fontFamily;
  double fontSize;
  double letterSpacing;
  double lineHeight;
  bool bold, italic;
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
    this.strokeColorValue = 0x00000000,
    this.strokeWidth = 0,
    this.shadowColorValue = 0x00000000,
    this.shadowBlur = 0,
    this.shadowOffsetX = 0,
    this.shadowOffsetY = 0,
    this.text = '',
    this.fontFamily = 'JameelNooriNastaleeq',
    this.fontSize = 56,
    this.letterSpacing = 0,
    this.lineHeight = 1.25,
    this.bold = false,
    this.italic = false,
    this.textAlign = TextAlign.center,
    this.textDirection = TextDirection.rtl,
    this.imageBytes,
    this.radius = 18,
  });

  Color get color => Color(colorValue);
  Color get strokeColor => Color(strokeColorValue);
  Color get shadowColor => Color(shadowColorValue);
  DesignElement clone() => DesignElement.fromJson(toJson());

  Map<String, dynamic> toJson() => {
        'id': id, 'kind': kind.name, 'x': x, 'y': y, 'width': width, 'height': height,
        'rotation': rotation, 'scaleX': scaleX, 'scaleY': scaleY, 'opacity': opacity,
        'locked': locked, 'hidden': hidden, 'color': colorValue,
        'strokeColor': strokeColorValue, 'strokeWidth': strokeWidth,
        'shadowColor': shadowColorValue, 'shadowBlur': shadowBlur,
        'shadowOffsetX': shadowOffsetX, 'shadowOffsetY': shadowOffsetY,
        'text': text, 'fontFamily': fontFamily, 'fontSize': fontSize,
        'letterSpacing': letterSpacing, 'lineHeight': lineHeight,
        'bold': bold, 'italic': italic, 'textAlign': textAlign.index,
        'textDirection': textDirection == TextDirection.rtl ? 'rtl' : 'ltr',
        'imageBytes': imageBytes == null ? null : base64Encode(imageBytes!), 'radius': radius,
      };

  factory DesignElement.fromJson(Map<String, dynamic> json) {
    final kindName = json['kind']?.toString();
    final kind = ElementKind.values.where((e) => e.name == kindName).firstOrNull ?? ElementKind.text;
    final alignIndex = (json['textAlign'] as num?)?.toInt() ?? TextAlign.center.index;
    final align = alignIndex >= 0 && alignIndex < TextAlign.values.length ? TextAlign.values[alignIndex] : TextAlign.center;
    Uint8List? bytes;
    final raw = json['imageBytes'];
    if (raw is String && raw.isNotEmpty) { try { bytes = base64Decode(raw); } catch (_) {} }
    final storedFont = json['fontFamily']?.toString();
    final fontFamily = storedFont == null || storedFont.isEmpty || storedFont == 'JameelNoori'
        ? 'JameelNooriNastaleeq'
        : storedFont;
    return DesignElement(
      id: json['id']?.toString() ?? '', kind: kind,
      x: (json['x'] as num?)?.toDouble() ?? 0, y: (json['y'] as num?)?.toDouble() ?? 0,
      width: (json['width'] as num?)?.toDouble() ?? 200, height: (json['height'] as num?)?.toDouble() ?? 100,
      rotation: (json['rotation'] as num?)?.toDouble() ?? 0, scaleX: (json['scaleX'] as num?)?.toDouble() ?? 1,
      scaleY: (json['scaleY'] as num?)?.toDouble() ?? 1, opacity: ((json['opacity'] as num?)?.toDouble() ?? 1).clamp(0, 1),
      locked: json['locked'] as bool? ?? false, hidden: json['hidden'] as bool? ?? false,
      colorValue: (json['color'] as num?)?.toInt() ?? 0xFFD4AF37,
      strokeColorValue: (json['strokeColor'] as num?)?.toInt() ?? 0,
      strokeWidth: ((json['strokeWidth'] as num?)?.toDouble() ?? 0).clamp(0, 40),
      shadowColorValue: (json['shadowColor'] as num?)?.toInt() ?? 0,
      shadowBlur: ((json['shadowBlur'] as num?)?.toDouble() ?? 0).clamp(0, 80),
      shadowOffsetX: (json['shadowOffsetX'] as num?)?.toDouble() ?? 0,
      shadowOffsetY: (json['shadowOffsetY'] as num?)?.toDouble() ?? 0,
      text: json['text']?.toString() ?? '', fontFamily: fontFamily,
      fontSize: ((json['fontSize'] as num?)?.toDouble() ?? 56).clamp(5, 100).toDouble(),
      letterSpacing: (json['letterSpacing'] as num?)?.toDouble() ?? 0,
      lineHeight: ((json['lineHeight'] as num?)?.toDouble() ?? 1.25).clamp(.7, 3),
      bold: json['bold'] as bool? ?? false, italic: json['italic'] as bool? ?? false,
      textAlign: align, textDirection: json['textDirection'] == 'ltr' ? TextDirection.ltr : TextDirection.rtl,
      imageBytes: bytes, radius: (json['radius'] as num?)?.toDouble() ?? 18,
    );
  }
}

class DesignPage {
  String title;
  CanvasSize size;
  Color background;
  List<DesignElement> elements;
  DesignPage({required this.title, required this.size, this.background = Colors.white, List<DesignElement>? elements}) : elements = elements ?? [];
  DesignPage clone() => DesignPage.fromJson(toJson());
  Map<String, dynamic> toJson() => {'title': title, 'size': size.toJson(), 'background': background.toARGB32(), 'elements': elements.map((e) => e.toJson()).toList()};
  factory DesignPage.fromJson(Map<String, dynamic> json) => DesignPage(
        title: json['title']?.toString() ?? 'Page', size: CanvasSize.fromJson(json['size'] as Map<String, dynamic>?),
        background: Color((json['background'] as num?)?.toInt() ?? Colors.white.toARGB32()),
        elements: json['elements'] is List ? (json['elements'] as List).whereType<Map>().map((e) => DesignElement.fromJson(Map<String, dynamic>.from(e))).toList() : [],
      );
}

class ProjectModel {
  String id;
  String name;
  int lastModified;
  List<DesignPage> pages;
  ProjectModel({required this.id, required this.name, required this.pages, int? lastModified}) : lastModified = lastModified ?? DateTime.now().millisecondsSinceEpoch;
  Map<String, dynamic> toJson() => {'schemaVersion': kSchemaVersion, 'id': id, 'name': name, 'lastModified': lastModified, 'pages': pages.map((p) => p.toJson()).toList()};
  factory ProjectModel.fromJson(Map<String, dynamic> json) => ProjectModel(
        id: json['id']?.toString() ?? '', name: json['name']?.toString() ?? 'Project', lastModified: (json['lastModified'] as num?)?.toInt(),
        pages: json['pages'] is List ? (json['pages'] as List).whereType<Map>().map((p) => DesignPage.fromJson(Map<String, dynamic>.from(p))).toList() : [],
      );
}

extension FirstOrNullExtension<T> on Iterable<T> { T? get firstOrNull => isEmpty ? null : first; }
