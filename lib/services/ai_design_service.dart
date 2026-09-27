import 'dart:convert';
import 'package:http/http.dart' as http;

class AiDesignPlan {
  final String title;
  final String style;
  final List<int> gradient;
  final String? providerMessage;

  const AiDesignPlan({
    required this.title,
    required this.style,
    required this.gradient,
    this.providerMessage,
  });

  factory AiDesignPlan.fromJson(Map<String, dynamic> json) {
    final colors = (json['gradient'] as List?)?.whereType<num>().map((e) => e.toInt()).toList();
    return AiDesignPlan(
      title: json['title']?.toString() ?? '',
      style: json['style']?.toString() ?? 'Premium',
      gradient: colors == null || colors.length < 2 ? const [0xFF10172D, 0xFF4C1D95] : colors,
      providerMessage: json['message']?.toString(),
    );
  }
}

abstract class AiDesignProvider {
  Future<AiDesignPlan> generate({
    required String prompt,
    required String style,
    required String ratio,
  });
}

class SecureEndpointAiProvider implements AiDesignProvider {
  final String endpoint;
  final Duration timeout;

  const SecureEndpointAiProvider({
    required this.endpoint,
    this.timeout = const Duration(seconds: 30),
  });

  @override
  Future<AiDesignPlan> generate({
    required String prompt,
    required String style,
    required String ratio,
  }) async {
    final response = await http
        .post(
          Uri.parse(endpoint),
          headers: const {'content-type': 'application/json'},
          body: jsonEncode({
            'prompt': prompt,
            'style': style,
            'ratio': ratio,
            'language': 'ur',
          }),
        )
        .timeout(timeout);

    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw Exception('AI provider returned HTTP ${response.statusCode}.');
    }

    final decoded = jsonDecode(response.body);
    if (decoded is! Map) {
      throw Exception('AI provider returned an invalid response.');
    }
    return AiDesignPlan.fromJson(Map<String, dynamic>.from(decoded));
  }
}

class LocalAiDesignProvider implements AiDesignProvider {
  const LocalAiDesignProvider();

  @override
  Future<AiDesignPlan> generate({
    required String prompt,
    required String style,
    required String ratio,
  }) async {
    final lower = prompt.toLowerCase();
    final islamic = style == 'Islamic' || lower.contains('اسلام') || lower.contains('quran');
    final school = style == 'School' || lower.contains('school') || lower.contains('مدرسہ');
    final youtube = style == 'YouTube' || ratio == '16:9';

    final gradient = islamic
        ? const [0xFF071F2A, 0xFF126E63, 0xFF1F8A70]
        : school
            ? const [0xFF102A43, 0xFF2563EB, 0xFF4F46E5]
            : youtube
                ? const [0xFF1B102F, 0xFF7C2D5A, 0xFFDB2777]
                : const [0xFF10172D, 0xFF292052, 0xFF4C1D95];

    return AiDesignPlan(
      title: prompt.trim(),
      style: style,
      gradient: gradient,
      providerMessage: 'Local design engine',
    );
  }
}

class AiDesignService {
  AiDesignService({
    AiDesignProvider? provider,
  }) : _provider = provider ?? _defaultProvider();

  final AiDesignProvider _provider;

  static AiDesignProvider _defaultProvider() {
    const endpoint = String.fromEnvironment('AI_DESIGN_ENDPOINT');
    if (endpoint.trim().isNotEmpty) {
      return SecureEndpointAiProvider(endpoint: endpoint);
    }
    return const LocalAiDesignProvider();
  }

  Future<AiDesignPlan> generate({
    required String prompt,
    required String style,
    required String ratio,
  }) {
    return _provider.generate(prompt: prompt, style: style, ratio: ratio);
  }
}
