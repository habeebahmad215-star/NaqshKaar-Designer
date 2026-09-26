import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

/// Backend-first AI gateway. Provider API keys should stay on the server.
/// For development only, AI_API_KEY can be supplied with --dart-define.
class AiService {
  AiService({
    http.Client? client,
    String? baseUrl,
    String? apiKey,
  })  : _client = client ?? http.Client(),
        _baseUrl = (baseUrl ?? const String.fromEnvironment('AI_BASE_URL')).replaceFirst(RegExp(r'/+$'), ''),
        _apiKey = apiKey ?? const String.fromEnvironment('AI_API_KEY');

  final http.Client _client;
  final String _baseUrl;
  final String _apiKey;

  bool get configured => _baseUrl.isNotEmpty;

  Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        if (_apiKey.isNotEmpty) 'Authorization': 'Bearer $_apiKey',
      };

  Future<String> write(String prompt, {String language = 'Urdu'}) async {
    final data = await _post('/write', {'prompt': prompt, 'language': language});
    final value = data['text'] ?? data['output'] ?? data['content'];
    if (value is! String || value.trim().isEmpty) {
      throw const FormatException('AI Write returned no text.');
    }
    return value.trim();
  }

  Future<Uint8List> generateImage(String prompt, {String? style}) async {
    return _decodeImage(await _post('/image', {
      'prompt': prompt,
      if (style != null && style.isNotEmpty) 'style': style,
    }));
  }

  Future<Uint8List> removeBackground(Uint8List bytes) async {
    return _decodeImage(await _post('/remove-background', {
      'image_base64': base64Encode(bytes),
    }));
  }

  Future<Uint8List> magicRemove(Uint8List bytes, {String? instruction}) async {
    return _decodeImage(await _post('/magic-remove', {
      'image_base64': base64Encode(bytes),
      if (instruction != null && instruction.trim().isNotEmpty) 'instruction': instruction.trim(),
    }));
  }

  Future<Uint8List> enhance(Uint8List bytes, {String? instruction}) async {
    return _decodeImage(await _post('/enhance', {
      'image_base64': base64Encode(bytes),
      if (instruction != null && instruction.trim().isNotEmpty) 'instruction': instruction.trim(),
    }));
  }

  Future<Map<String, dynamic>> _post(String path, Map<String, dynamic> body) async {
    if (!configured) {
      throw StateError('AI is not configured. Set AI_BASE_URL to your secure AI gateway.');
    }
    final response = await _client
        .post(Uri.parse('$_baseUrl$path'), headers: _headers, body: jsonEncode(body))
        .timeout(const Duration(seconds: 90));
    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw HttpException('AI request failed (${response.statusCode}): ${response.body}');
    }
    final decoded = jsonDecode(response.body);
    if (decoded is! Map<String, dynamic>) {
      throw const FormatException('AI gateway returned invalid JSON.');
    }
    return decoded;
  }

  Uint8List _decodeImage(Map<String, dynamic> data) {
    final value = data['image_base64'] ?? data['image'] ?? data['data'];
    if (value is! String || value.isEmpty) {
      throw const FormatException('AI gateway returned no image.');
    }
    final normalized = value.contains(',') ? value.substring(value.indexOf(',') + 1) : value;
    return base64Decode(normalized);
  }

  void dispose() => _client.close();
}

String aiConfigurationHint() => kDebugMode
    ? 'Connect a secure AI gateway with --dart-define=AI_BASE_URL=...'
    : 'AI service is not configured for this build.';

class HttpException implements Exception {
  const HttpException(this.message);
  final String message;

  @override
  String toString() => message;
}
