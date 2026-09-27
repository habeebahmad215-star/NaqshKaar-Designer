import 'dart:html' as html;
import 'dart:typed_data';

Future<void> saveImageBytes(Uint8List bytes, String name) async {
  final blob = html.Blob(<dynamic>[bytes], 'application/octet-stream');
  final url = html.Url.createObjectUrlFromBlob(blob);
  final anchor = html.AnchorElement(href: url)
    ..download = name
    ..style.display = 'none';
  html.document.body?.children.add(anchor);
  anchor.click();
  anchor.remove();
  html.Url.revokeObjectUrl(url);
}
