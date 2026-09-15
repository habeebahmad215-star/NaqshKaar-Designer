import 'dart:typed_data';
import 'dart:ui' as ui;

import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:gal/gal.dart';
import 'package:image/image.dart' as img;
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;
import 'package:printing/printing.dart';
import 'package:flutter/services.dart' show rootBundle;

import '../models/design_models.dart';

class ExportService {
  static const int _maxRasterPixels = 4096 * 4096;

  Future<Uint8List> capturePng(GlobalKey key, double logicalWidth, double targetWidth) async {
    final boundary = key.currentContext?.findRenderObject() as RenderRepaintBoundary?;
    if (boundary == null) throw StateError('Canvas is not ready for export.');
    if (!boundary.hasSize) throw StateError('Canvas has not finished rendering.');

    // Rendering a very large artboard at a device-independent pixel ratio can
    // allocate hundreds of MB and kill the Android process. Keep ordinary
    // 1080/2048/4096 designs at their requested width, while safely limiting
    // extreme custom canvases to a maximum raster budget.
    final logicalHeight = boundary.size.height;
    final requestedRatio = targetWidth / logicalWidth;
    final safeRatio = logicalWidth <= 0 || logicalHeight <= 0
        ? requestedRatio
        : mathMin(requestedRatio, mathSqrt(_maxRasterPixels / (logicalWidth * logicalHeight)));
    final ratio = safeRatio.clamp(0.25, 8.0).toDouble();
    final image = await boundary.toImage(pixelRatio: ratio);
    try {
      final data = await image.toByteData(format: ui.ImageByteFormat.png);
      if (data == null) throw StateError('Could not encode PNG.');
      return data.buffer.asUint8List();
    } finally {
      image.dispose();
    }
  }

  double mathMin(double a, double b) => a < b ? a : b;
  double mathSqrt(double value) => value <= 0 ? 0 : value.sqrt();

  Future<Uint8List> pngToJpeg(Uint8List pngBytes, {int quality = 95}) async {
    final decoded = img.decodeImage(pngBytes);
    if (decoded == null) throw StateError('Could not decode rendered image.');
    return Uint8List.fromList(img.encodeJpg(decoded, quality: quality));
  }

  Future<void> _ensureGalleryAccess() async {
    if (await Gal.hasAccess()) return;
    if (!await Gal.requestAccess()) throw StateError('Gallery permission was denied.');
  }

  Future<void> savePng(Uint8List bytes, String name) async {
    await _ensureGalleryAccess();
    await Gal.putImageBytes(bytes, name: name);
  }

  Future<void> saveJpeg(Uint8List bytes, String name) async {
    await _ensureGalleryAccess();
    await Gal.putImageBytes(bytes, name: name);
  }

  Future<void> exportPng(DesignPage page, GlobalKey key) async {
    final bytes = await capturePng(key, page.size.width, page.size.width);
    await savePng(bytes, 'naqshkaar_design.png');
  }

  Future<void> exportJpg(DesignPage page, GlobalKey key) async {
    final png = await capturePng(key, page.size.width, page.size.width);
    final jpg = await pngToJpeg(png);
    await saveJpeg(jpg, 'naqshkaar_design.jpg');
  }

  String _safeName(String value) {
    final cleaned = value.replaceAll(RegExp(r'[\\/:*?"<>|]'), '_').trim();
    return cleaned.isEmpty ? 'naqshkaar_design' : cleaned;
  }

  /// Creates a PDF from the already-rendered Flutter canvas.
  ///
  /// This is intentionally the primary PDF export path for NaqshKaar. Urdu
  /// Nastaliq shaping, glyph positioning, line height, shadows, rotation,
  /// opacity, image cropping and every future canvas effect are first rendered
  /// by Flutter and then placed 1:1 into the PDF as a page image. This avoids
  /// a second text-layout engine silently clipping or reshaping Urdu.
  Future<void> shareRenderedPdf({
    required ProjectModel project,
    required List<Uint8List> pagePngs,
  }) async {
    if (project.pages.isEmpty) throw StateError('Project has no pages.');
    if (pagePngs.length != project.pages.length) {
      throw StateError('PDF export could not render every page.');
    }

    final doc = pw.Document();
    for (var i = 0; i < project.pages.length; i++) {
      final page = project.pages[i];
      final image = pw.MemoryImage(pagePngs[i]);
      doc.addPage(
        pw.Page(
          pageFormat: PdfPageFormat(page.size.width, page.size.height),
          margin: pw.EdgeInsets.zero,
          build: (_) => pw.SizedBox(
            width: page.size.width,
            height: page.size.height,
            child: pw.Image(image, fit: pw.BoxFit.fill),
          ),
        ),
      );
    }

    await Printing.sharePdf(
      bytes: await doc.save(),
      filename: '${_safeName(project.name)}.pdf',
    );
  }

  // Kept as a model-based fallback for callers that need a selectable-text PDF.
  // The workspace uses shareRenderedPdf so the exported PDF matches the canvas.
  Future<void> sharePdf(ProjectModel project) async {
    if (project.pages.isEmpty) throw StateError('Project has no pages.');
    final doc = pw.Document();
    final fontCache = <String, pw.Font>{};

    Future<pw.Font> fontFor(String family) async {
      final normalized = family == 'NotoNastaliqUrdu' ? family : 'Gulzar';
      final cached = fontCache[normalized];
      if (cached != null) return cached;
      final asset = normalized == 'NotoNastaliqUrdu'
          ? 'assets/fonts/NotoNastaliqUrdu-Regular.ttf'
          : 'assets/fonts/Gulzar-Regular.ttf';
      final bytes = await rootBundle.load(asset);
      final loaded = pw.Font.ttf(bytes);
      fontCache[normalized] = loaded;
      return loaded;
    }

    for (final page in project.pages) {
      final textFonts = <String, pw.Font>{};
      for (final e in page.elements.where((e) => !e.hidden && e.kind == ElementKind.text)) {
        textFonts[e.id] = await fontFor(e.fontFamily);
      }
      doc.addPage(
        pw.Page(
          pageFormat: PdfPageFormat(page.size.width, page.size.height),
          margin: pw.EdgeInsets.zero,
          build: (_) => pw.Container(
            width: page.size.width,
            height: page.size.height,
            color: PdfColor.fromInt(page.background.toARGB32()),
            child: pw.Stack(
              children: [
                for (final e in page.elements.where((e) => !e.hidden))
                  if (e.kind == ElementKind.shape)
                    pw.Positioned(
                      left: e.x,
                      top: e.y,
                      child: pw.SizedBox(
                        width: e.width,
                        height: e.height,
                        child: pw.Container(
                          decoration: pw.BoxDecoration(
                            color: PdfColor.fromInt(e.colorValue),
                            borderRadius: pw.BorderRadius.circular(e.radius),
                          ),
                        ),
                      ),
                    )
                  else if (e.kind == ElementKind.image && e.imageBytes != null)
                    pw.Positioned(
                      left: e.x,
                      top: e.y,
                      child: pw.SizedBox(
                        width: e.width,
                        height: e.height,
                        child: pw.Image(pw.MemoryImage(e.imageBytes!), fit: pw.BoxFit.cover),
                      ),
                    )
                  else if (e.kind == ElementKind.text)
                    pw.Positioned(
                      left: e.x,
                      top: e.y,
                      child: pw.Container(
                        width: e.width,
                        child: pw.Text(
                          e.text.isEmpty ? 'Text' : e.text,
                          textAlign: _pdfAlign(e.textAlign),
                          textDirection: e.textDirection == TextDirection.rtl ? pw.TextDirection.rtl : pw.TextDirection.ltr,
                          style: pw.TextStyle(
                            font: textFonts[e.id],
                            fontSize: e.fontSize,
                            fontWeight: e.bold ? pw.FontWeight.bold : pw.FontWeight.normal,
                            fontStyle: e.italic ? pw.FontStyle.italic : pw.FontStyle.normal,
                            color: PdfColor.fromInt(e.colorValue),
                            letterSpacing: e.letterSpacing,
                          ),
                        ),
                      ),
                    ),
              ],
            ),
          ),
        ),
      );
    }
    await Printing.sharePdf(bytes: await doc.save(), filename: '${_safeName(project.name)}.pdf');
  }

  pw.TextAlign _pdfAlign(TextAlign align) {
    switch (align) {
      case TextAlign.left:
      case TextAlign.start:
        return pw.TextAlign.left;
      case TextAlign.right:
      case TextAlign.end:
        return pw.TextAlign.right;
      case TextAlign.justify:
        return pw.TextAlign.justify;
      case TextAlign.center:
        return pw.TextAlign.center;
    }
  }
}
