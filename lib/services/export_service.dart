import 'dart:typed_data';
import 'dart:ui' as ui;
import 'package:flutter/rendering.dart';
import 'package:image/image.dart' as img;
import 'package:image_gallery_saver/image_gallery_saver.dart';
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;
import 'package:printing/printing.dart';

class ExportService {
  Future<Uint8List> capturePng(
    GlobalKey key,
    double logicalWidth,
    double targetWidth,
  ) async {
    final boundary =
        key.currentContext?.findRenderObject()
            as RenderRepaintBoundary?;

    if (boundary == null) {
      throw StateError('Canvas is not ready for export.');
    }

    final ratio = targetWidth / logicalWidth;

    final image = await boundary.toImage(
      pixelRatio: ratio,
    );

    final data = await image.toByteData(
      format: ui.ImageByteFormat.png,
    );

    image.dispose();

    if (data == null) {
      throw StateError('Could not encode PNG.');
    }

    return data.buffer.asUint8List();
  }

  Future<Uint8List> pngToJpeg(
    Uint8List pngBytes, {
    int quality = 95,
  }) async {
    final decoded = img.decodeImage(pngBytes);

    if (decoded == null) {
      throw StateError('Could not decode rendered image.');
    }

    final jpg = img.encodeJpg(
      decoded,
      quality: quality,
    );

    return Uint8List.fromList(jpg);
  }

  Future<void> savePng(
    Uint8List bytes,
    String name,
  ) async {
    final result = await ImageGallerySaver.saveImage(
      bytes,
      quality: 100,
      name: name,
    );

    if (result is Map &&
        result['isSuccess'] == false) {
      throw StateError('Gallery save failed.');
    }
  }

  Future<void> saveJpeg(
    Uint8List bytes,
    String name,
  ) async {
    final result = await ImageGallerySaver.saveImage(
      bytes,
      quality: 100,
      name: name,
      isReturnImagePathOfIOS: true,
    );

    if (result is Map &&
        result['isSuccess'] == false) {
      throw StateError('Gallery save failed.');
    }
  }

  Future<void> sharePdf(
    Uint8List pngBytes,
    double width,
    double height,
    String filename,
  ) async {
    final doc = pw.Document();

    doc.addPage(
      pw.Page(
        pageFormat: PdfPageFormat(
          width,
          height,
        ),
        margin: pw.EdgeInsets.zero,
        build: (_) => pw.Image(
          pw.MemoryImage(pngBytes),
          fit: pw.BoxFit.fill,
        ),
      ),
    );

    await Printing.sharePdf(
      bytes: await doc.save(),
      filename: filename,
    );
  }
}
