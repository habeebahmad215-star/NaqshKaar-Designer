import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;
import 'package:http/io_client.dart';

/// Native AI transport with normal DNS first and a DNS-over-HTTPS fallback.
/// The HTTPS request keeps the real Vercel hostname for TLS/SNI while the
/// socket can connect to a freshly resolved IPv4 address.
List<http.Client> createPlatformAiClients() {
  final clients = <http.Client>[
    IOClient(
      HttpClient()
        ..connectionTimeout = const Duration(seconds: 8)
        ..idleTimeout = const Duration(seconds: 20),
    ),
  ];

  for (var index = 0; index < 3; index++) {
    final HttpClient client = HttpClient();
    client.connectionTimeout = const Duration(seconds: 8);
    client.idleTimeout = const Duration(seconds: 20);
    client.findProxy = (Uri _) => 'DIRECT';
    client.connectionFactory = (
      Uri uri,
      String? proxyHost,
      int? proxyPort,
    ) async {
      if (proxyHost != null || proxyPort != null) {
        return Socket.startConnect(uri.host, uri.port);
      }

      final ips = await _gatewayIps();
      if (ips.isEmpty) {
        return Socket.startConnect(uri.host, uri.port);
      }
      final ip = ips[index % ips.length];
      return Socket.startConnect(
        InternetAddress(ip, type: InternetAddressType.IPv4),
        uri.port,
      );
    };
    clients.add(IOClient(client));
  }

  return clients;
}

Future<List<String>>? _ipsFuture;

Future<List<String>> _gatewayIps() {
  return _ipsFuture ??= _resolveGatewayIps();
}

Future<List<String>> _resolveGatewayIps() async {
  final uri = Uri.https(
    'cloudflare-dns.com',
    '/dns-query',
    <String, String>{
      'name': 'naqsh-kaar-designer-9g3r.vercel.app',
      'type': 'A',
    },
  );
  final client = HttpClient()
    ..connectionTimeout = const Duration(seconds: 8)
    ..idleTimeout = const Duration(seconds: 10);
  try {
    final request = await client.getUrl(uri);
    request.headers.set(HttpHeaders.acceptHeader, 'application/dns-json');
    final response = await request.close();
    if (response.statusCode != HttpStatus.ok) return const <String>[];
    final body = await response.transform(utf8.decoder).join();
    final json = jsonDecode(body);
    final answer = json is Map<String, dynamic> ? json['Answer'] : null;
    if (answer is! List) return const <String>[];
    return answer
        .whereType<Map>()
        .where((item) => item['type'] == 1 && item['data'] is String)
        .map((item) => item['data'] as String)
        .where((ip) => ip.isNotEmpty)
        .toSet()
        .toList();
  } catch (_) {
    return const <String>[];
  } finally {
    client.close(force: true);
  }
}
