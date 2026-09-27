import 'package:gal/gal.dart';
import 'dart:typed_data';

Future<void> saveImageBytes(Uint8List bytes, String name) async {
  if (!await Gal.hasAccess() && !await Gal.requestAccess()) {
    throw StateError('Gallery permission was denied.');
  }
  await Gal.putImageBytes(bytes, name: name);
}
