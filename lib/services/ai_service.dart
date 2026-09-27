import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter/foundation.dart';

import 'ai_http_clients.dart';
import 'package:http/http.dart' as http;

/// Backend-first AI gateway. Provider API keys stay on the server.
class AiService {
  AiService({
    http.Client? client,
    String? baseUrl,
    String? apiKey,
  })  : _client = client ?? http.Client(),
        _baseUrl = _resolveBaseUrl(baseUrl),
        _apiKey = apiKey ?? const String.fromEnvironment('AI_API_KEY');

  final String _baseUrl;
  final List<http.Client> _clients;
  final String _apiKey;

  static const String _productionGateway =
      'https://naqsh-kaar-designer-9g3r.vercel.app/api';

  static String _resolveBaseUrl(String? baseUrl) {
    final explicit =
        (baseUrl ?? const String.fromEnvironment('AI_BASE_URL')).trim();
    if (explicit.isNotEmpty) {
      return explicit.replaceFirst(RegExp(r'/+$'), '');
    }
    return kIsWeb ? '/api' : _productionGateway;
  }

  bool get configured => _baseUrl.isNotEmpty;

  Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        if (_apiKey.isNotEmpty) 'Authorization': 'Bearer $_apiKey',
      };

  Future<String> write(String prompt, {String language = 'Urdu'}) async {
    final data = await _post('/write', {
      'prompt': prompt,
      'language': language,
    });
    final value = data['text'] ?? data['output'] ?? data['content'];
    if (value is! String || value.trim().isEmpty) {
      throw const FormatException('AI Write returned no text.');
    }
    return value.trim();
  }

  Future<Uint8List> generateImage(
    String prompt, {
    String? style,
    String? size,
  }) async {
    return _decodeImage(await _post('/image', {
      'prompt': prompt,
      if (style != null && style.isNotEmpty) 'style': style,
      if (size != null && size.isNotEmpty) 'size': size,
    }));
  }

  Future<Uint8List> removeBackground(Uint8List bytes) async {
    return _decodeImage(await _post('/remove-background', {
      'image_base64': base64Encode(bytes),
    }));
  }

  Future<Uint8List> magicRemove(
    Uint8List bytes, {
    String? instruction,
  }) async {
    return _decodeImage(await _post('/magic-remove', {
      'image_base64': base64Encode(bytes),
      if (instruction != null && instruction.trim().isNotEmpty)
        'instruction': instruction.trim(),
    }));
  }

  Future<Uint8List> enhance(
    Uint8List bytes, {
    String? instruction,
  }) async {
    return _decodeImage(await _post('/enhance', {
      'image_base64': base64Encode(bytes),
      if (instruction != null && instruction.trim().isNotEmpty)
        'instruction': instruction.trim(),
    }));
  }

  Future<Map<String, dynamic>> _post(
    String path,
    Map<String, dynamic> body,
  ) async {
    if (!configured) {
      throw StateError('AI gateway is not configured.');
    }

    Object? lastError;
    http.Response? response;
    for (final client in _clients) {
      try {
        response = await client
            .post(
              Uri.parse('$_baseUrl$path'),
              headers: _headers,
              body: jsonEncode(body),
            )
            .timeout(const Duration(seconds: 90));

        if (response.statusCode >= 200 && response.statusCode < 300) {
          break;
        }
        if (response.statusCode >= 400 && response.statusCode < 600) {
          throw HttpException(
            'AI request failed (${response.statusCode}): ${response.body}',
          );
        }
      } catch (error) {
        lastError = error;
        response = null;
        if (kIsWeb) rethrow;
      }
    }

    if (response == null) {
      throw HttpException(
        'AI gateway could not be reached. Network/DNS error: $lastError',
      );
    }

    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw HttpException(
        'AI request failed (${response.statusCode}): ${response.body}',
      );
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
    final normalized =
        value.contains(',') ? value.substring(value.indexOf(',') + 1) : value;
    return base64Decode(normalized);
  }

  void dispose() {
    for (final client in _clients) {
      client.close();
    }
  }
}

String aiConfigurationHint() => kDebugMode
    ? 'Connect a secure AI gateway with --dart-define=AI_BASE_URL=...'
    : 'AI service is connected through the secure gateway.';

class HttpException implements Exception {
  const HttpException(this.message);

  final String message;

  @override
  String toString() => message;
}
