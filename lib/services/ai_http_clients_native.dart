import 'dart:io';

import 'package:http/http.dart' as http;
import 'package:http/io_client.dart';

/// Native fallback for networks whose DNS resolver cannot resolve Vercel
/// deployment hostnames. The HTTPS request still uses the real gateway
/// hostname, preserving normal TLS certificate/SNI validation.
List<http.Client> createPlatformAiClients() {
  const ips = <String>[
    '216.198.79.67',
    '64.29.17.67',
    '216.198.79.65',
    '64.29.17.65',
    '216.198.79.1',
    '64.29.17.1',
    '76.76.21.21',
  ];

  final clients = <http.Client>[
    IOClient(
      HttpClient()
        ..connectionTimeout = const Duration(seconds: 8)
        ..idleTimeout = const Duration(seconds: 15),
    ),
  ];

  for (final ip in ips) {
    final client = HttpClient()
      ..connectionTimeout = const Duration(seconds: 8)
      ..idleTimeout = const Duration(seconds: 15);
    client.findProxy = (Uri _) => 'DIRECT';
    client.connectionFactory = (
        Uri uri,
        String? proxyHost,
        int? proxyPort,
      ) {
        if (proxyHost != null || proxyPort != null) {
          return Socket.startConnect(uri.host, uri.port);
        }
        return Socket.startConnect(
          InternetAddress(ip, type: InternetAddressType.IPv4),
          uri.port,
        );
      };
    clients.add(IOClient(client));
  }

  return clients;
}
