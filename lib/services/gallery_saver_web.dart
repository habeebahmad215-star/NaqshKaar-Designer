import 'dart:js_interop';
import 'dart:typed_data';

import 'package:web/web.dart';

Future<void> saveImageBytes(Uint8List bytes, String name) async {
  final blob = Blob(
    <JSAny>[bytes.toJS].toJS,
    BlobPropertyBag(type: 'application/octet-stream'),
  );
  final url = URL.createObjectURL(blob);
  final anchor = HTMLAnchorElement()
    ..href = url
    ..download = name
    ..style.display = 'none';
  document.body?.append(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}
