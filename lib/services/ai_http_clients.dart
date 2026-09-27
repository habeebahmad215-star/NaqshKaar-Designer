import 'package:http/http.dart' as http;

import 'ai_http_clients_native.dart'
    if (dart.library.js_interop) 'ai_http_clients_web.dart';

List<http.Client> createAiClients() => createPlatformAiClients();
