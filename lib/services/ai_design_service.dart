import 'dart:typed_data';

import 'ai_service.dart';

class AiDesignPlan {
  final String title;
  final String style;
  final List<int> gradient;
  final String? providerMessage;
  final Uint8List? imageBytes;

  const AiDesignPlan({
    required this.title,
    required this.style,
    required this.gradient,
    this.providerMessage,
    this.imageBytes,
  });
}

class AiDesignService {
  AiDesignService({AiService? service}) : _service = service ?? AiService();

  final AiService _service;

  Future<AiDesignPlan> generate({
    required String prompt,
    required String style,
    required String ratio,
  }) async {
    final size = switch (ratio) {
      '16:9' => '1536x1024',
      '9:16' => '1024x1536',
      '4:5' => '1080x1350',
      _ => '1024x1024',
    };
    final bytes = await _service.generateImage(
      _buildPrompt(prompt, style, ratio),
      style: style,
      size: size,
    );
    return AiDesignPlan(
      title: prompt.trim(),
      style: style,
      gradient: const [0xFF10172D, 0xFF4C1D95],
      providerMessage: _service.lastProvider == 'AI' ? 'AI artwork ready' : '${_service.lastProvider} artwork ready',
      imageBytes: bytes,
    );
  }

  String _buildPrompt(String prompt, String style, String ratio) {
    return '''Create a premium professional graphic-design composition for NaqshKaar Designer.
Style: $style.
Requested canvas ratio: $ratio.
User brief: $prompt

Design requirements:
- polished commercial graphic-design composition, not a plain illustration;
- strong hierarchy, balanced spacing, premium lighting, depth and clean edges;
- use an elegant Urdu/Islamic/modern visual language when appropriate;
- create a clean, intentional area for the exact headline that NaqshKaar will overlay separately;
- do not invent fake Urdu copy or tiny unreadable paragraphs;
- prioritize background, decorative elements, composition and visual atmosphere;
- no watermarks, logos or random gibberish text.''';
  }

  void dispose() => _service.dispose();
}
