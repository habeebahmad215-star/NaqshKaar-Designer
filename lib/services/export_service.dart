import 'dart:typed_data';
import 'dart:ui' as ui;

import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:gal/gal.dart';
import 'package:image/image.dart' as img;
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;
import 'package:printing/printing.dart';

import '../models/design_models.dart';

class ExportService {
  Future<Uint8List> capturePng(GlobalKey key, double logicalWidth, double targetWidth) async {
    final boundary = key.currentContext?.findRenderObject() as RenderRepaintBoundary?;
    if (boundary == null) throw StateError('Canvas is not ready for export.');
    final ratio = targetWidth / logicalWidth;
    final image = await boundary.toImage(pixelRatio: ratio);
    final data = await image.toByteData(format: ui.ImageByteFormat.png);
    image.dispose();
    if (data == null) throw StateError('Could not encode PNG.');
    return data.buffer.asUint8List();
  }

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

  // Compatibility helpers used by the current workspace export menu.
  Future<void> exportPng(ProjectModel project, GlobalKey key) async {
    if (project.pages.isEmpty) throw StateError('Project has no pages.');
    final page = project.pages.first;
    final bytes = await capturePng(key, page.size.width, page.size.width);
    await savePng(bytes, '${_safeName(project.name)}.png');
  }

  Future<void> exportJpg(ProjectModel project, GlobalKey key) async {
    if (project.pages.isEmpty) throw StateError('Project has no pages.');
    final page = project.pages.first;
    final png = await capturePng(key, page.size.width, page.size.width);
    final jpg = await pngToJpeg(png);
    await saveJpeg(jpg, '${_safeName(project.name)}.jpg');
  }

  String _safeName(String value) {
    final cleaned = value.replaceAll(RegExp(r'[\\/:*?"<>|]'), '_').trim();
    return cleaned.isEmpty ? 'naqshkaar_design' : cleaned;
  }

  Future<void> sharePdf(ProjectModel project) async {
    if (project.pages.isEmpty) throw StateError('Project has no pages.');
    final doc = pw.Document();
    for (final page in project.pages) {
      doc.addPage(
        pw.Page(
          pageFormat: PdfPageFormat(page.size.width, page.size.height),
          margin: pw.EdgeInsets.zero,
          build: (_) => pw.Container(
            color: PdfColor.fromInt(page.background.toARGB32()),
            child: pw.Stack(
              children: [
                for (final e in page.elements.where((e) => !e.hidden))
                  if (e.kind == ElementKind.shape)
                    pw.Positioned(
                      left: e.x, top: e.y, width: e.width, height: e.height,
                      child: pw.Container(
                        decoration: pw.BoxDecoration(
                          color: PdfColor.fromInt(e.colorValue),
                          borderRadius: pw.BorderRadius.circular(e.radius),
                        ),
                      ),
                    )
                  else if (e.kind == ElementKind.image && e.imageBytes != null)
                    pw.Positioned(
                      left: e.x, top: e.y, width: e.width, height: e.height,
                      child: pw.Image(pw.MemoryImage(e.imageBytes!), fit: pw.BoxFit.fill),
                    )
                  else if (e.kind == ElementKind.text)
                    pw.Positioned(
                      left: e.x, top: e.y, width: e.width, height: e.height,
                      child: pw.Text(
                        e.text,
                        textAlign: _pdfAlign(e.textAlign),
                        style: pw.TextStyle(
                          fontSize: e.fontSize,
                          fontWeight: e.bold ? pw.FontWeight.bold : pw.FontWeight.normal,
                          fontStyle: e.italic ? pw.FontStyle.italic : pw.FontStyle.normal,
                          color: PdfColor.fromInt(e.colorValue),
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
      case TextAlign.left: return pw.TextAlign.left;
      case TextAlign.right: return pw.TextAlign.right;
      case TextAlign.justify: return pw.TextAlign.justify;
      case TextAlign.center: return pw.TextAlign.center;
    }
  }
}
