import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;
import 'package:http/io_client.dart';

/// Native AI transport.
///
/// Android devices can occasionally fail to resolve a Vercel deployment
/// hostname even while the same URL works in the browser. The transport
/// therefore uses normal DNS first, then several DNS-over-HTTPS resolvers,
/// and finally Vercel's documented anycast IPv4 address as a last-resort
/// direct socket target. The request URI keeps the real hostname so TLS/SNI
/// and HTTP Host routing remain correct.
List<http.Client> createPlatformAiClients() {
  final clients = <http.Client>[
    IOClient(
      HttpClient()
        ..connectionTimeout = const Duration(seconds: 8)
        ..idleTimeout = const Duration(seconds: 20),
    ),
  ];

  for (var index = 0; index < 4; index++) {
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
        return Socket.startConnect(
          InternetAddress(_vercelFallbackIp, type: InternetAddressType.IPv4),
          uri.port,
        );
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

const String _gatewayHost = 'naqsh-kaar-designer-9g3r.vercel.app';

// Vercel documents 76.76.21.21 as its general-purpose anycast IPv4.
// Keep it only as a last-resort transport address; the URI host remains
// _gatewayHost so TLS/SNI and Vercel routing still use the hostname.
const String _vercelFallbackIp = '76.76.21.21';

Future<List<String>> _gatewayIps() async {
  final results = <String>{};

  for (final resolver in _dnsResolvers) {
    final ips = await _resolveWithResolver(resolver);
    results.addAll(ips);
    if (results.length >= 4) break;
  }

  return results.toList(growable: false);
}

const List<String> _dnsResolvers = <String>[
  'cloudflare-dns.com',
  'dns.google',
  'dns.quad9.net',
  'dns.adguard-dns.com',
];

Future<List<String>> _resolveWithResolver(String resolver) async {
  final uri = Uri.https(
    resolver,
    '/resolve',
    <String, String>{
      'name': _gatewayHost,
      'type': 'A',
    },
  );

  final client = HttpClient()
    ..connectionTimeout = const Duration(seconds: 6)
    ..idleTimeout = const Duration(seconds: 8);

  try {
    final request = await client.getUrl(uri);
    request.headers.set(HttpHeaders.acceptHeader, 'application/dns-json');
    final response = await request.close();
    if (response.statusCode != HttpStatus.ok) {
      return const <String>[];
    }

    final body = await response.transform(utf8.decoder).join();
    final decoded = jsonDecode(body);
    final answer = decoded is Map<String, dynamic> ? decoded['Answer'] : null;
    if (answer is! List) return const <String>[];

    return answer
        .whereType<Map>()
        .where((item) => item['type'] == 1 && item['data'] is String)
        .map((item) => item['data'] as String)
        .where((ip) => ip.isNotEmpty)
        .toSet()
        .toList(growable: false);
  } catch (_) {
    return const <String>[];
  } finally {
    client.close(force: true);
  }
}
