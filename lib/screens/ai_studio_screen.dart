import 'package:flutter/material.dart';

import '../models/design_models.dart';
import '../services/ai_design_service.dart';
import 'workspace_screen.dart';

class AiStudioScreen extends StatefulWidget {
  const AiStudioScreen({super.key});
  @override State<AiStudioScreen> createState() => _AiStudioScreenState();
}

class _AiStudioScreenState extends State<AiStudioScreen> {
  final TextEditingController _prompt = TextEditingController(text: 'ایک خوبصورت اسلامی پوسٹر بنائیں');
  static const _ink = Color(0xFF111827);
  static const _muted = Color(0xFF718096);
  static const _purple = Color(0xFF6D28D9);
  static const _blue = Color(0xFF2563EB);
  String _style = 'Premium';
  String _ratio = '1:1';
  bool _generating = false;
  bool _generated = false;
  String _status = 'Ready';
  AiDesignPlan? _plan;
  final AiDesignService _ai = AiDesignService();

  final List<String> _styles = const ['Premium','Islamic','Minimal','Luxury','School','YouTube'];
  final List<Map<String, String>> _presetItems = const [
    {'title': 'Islamic Poster', 'icon': '☪'},
    {'title': 'School Admission', 'icon': '🎓'},
    {'title': 'Naat Invitation', 'icon': '✦'},
    {'title': 'YouTube Thumbnail', 'icon': '▶'},
  ];

  @override void dispose() { _prompt.dispose(); _ai.dispose(); super.dispose(); }

  Future<void> _generate() async {
    final prompt = _prompt.text.trim();
    if (prompt.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please describe your design first.')));
      return;
    }
    setState(() { _generating = true; _generated = false; _status = 'Generating with AI…'; });
    try {
      final plan = await _ai.generate(prompt: prompt, style: _style, ratio: _ratio);
      if (!mounted) return;
      setState(() {
        _plan = plan;
        _generating = false;
        _generated = plan.imageBytes != null;
        _status = plan.providerMessage ?? 'Generated';
      });
    } catch (error) {
      if (!mounted) return;
      setState(() { _generating = false; _status = 'AI unavailable'; });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('AI generation failed. Please try again.')),
      );
    }
  }

  void _useInCanvas() {
    final bytes = _plan?.imageBytes;
    if (bytes == null) return;
    final size = switch (_ratio) {
      '4:5' => const CanvasSize(1080, 1350),
      '16:9' => const CanvasSize(1280, 720),
      '9:16' => const CanvasSize(1080, 1920),
      _ => const CanvasSize(1080, 1080),
    };
    final headline = _prompt.text.trim();
    final project = ProjectModel(
      id: 'ai_' + DateTime.now().microsecondsSinceEpoch.toString(),
      name: 'AI Design — ' + headline.split('\n').first,
      pages: [
        DesignPage(
          title: 'AI Generated',
          size: size,
          background: const Color(0xFF10172D),
          elements: [
            DesignElement(
              id: 'ai_artwork',
              kind: ElementKind.image,
              x: 0, y: 0, width: size.width, height: size.height,
              imageBytes: bytes,
            ),
            DesignElement(
              id: 'ai_heading',
              kind: ElementKind.text,
              x: size.width * .08, y: size.height * .30,
              width: size.width * .84, height: size.height * .25,
              text: headline,
              fontSize: size.width > 1100 ? 78 : 64,
              colorValue: Colors.white.toARGB32(),
              fontFamily: 'JameelNooriNastaleeq',
              bold: true, textAlign: TextAlign.center,
              textDirection: TextDirection.rtl,
              shadowColorValue: Colors.black54.toARGB32(),
              shadowBlur: 14,
              shadowOffsetY: 4,
            ),
            DesignElement(
              id: 'ai_accent',
              kind: ElementKind.shape,
              x: size.width * .20, y: size.height * .66,
              width: size.width * .60, height: 8,
              colorValue: const Color(0xFFD4AF37).toARGB32(), radius: 8,
            ),
          ],
        ),
      ],
    );
    Navigator.of(context).push(MaterialPageRoute<void>(
      builder: (_) => WorkspaceScreen(initialProject: project),
    ));
  }

  @override Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF7F8FC),
      appBar: AppBar(
        title: const Text('AI Studio'),
        actions: [IconButton(tooltip: 'AI settings', onPressed: _showInfo, icon: const Icon(Icons.tune_rounded))],
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(16, 10, 16, 28),
          child: CustomScrollView(
          slivers: [
            SliverToBoxAdapter(child: _hero()),
            SliverToBoxAdapter(child: _section('Describe your design', 'Urdu, Hindi or English — write naturally.')),
            SliverToBoxAdapter(child: _promptBox()),
            SliverToBoxAdapter(child: _presets()),
            SliverToBoxAdapter(child: _section('Style', 'Choose the visual direction.')),
            SliverToBoxAdapter(child: _styleChips()),
            SliverToBoxAdapter(child: _section('Canvas ratio', 'Optimized presets for social and print.')),
            SliverToBoxAdapter(child: _ratioChips()),
            SliverToBoxAdapter(child: _generateButton()),
            if (_generating) SliverToBoxAdapter(child: _generationProgress()),
            if (_generated) SliverToBoxAdapter(child: _resultCard()),
          ],
        ),
        ),
      ),
    );
  }

  Widget _hero() => Container(
    margin: const EdgeInsets.only(bottom: 22),
    decoration: BoxDecoration(
      borderRadius: BorderRadius.circular(26),
      gradient: const LinearGradient(begin: Alignment.topLeft, end: Alignment.bottomRight,
        colors: [Color(0xFF17112E), Color(0xFF31206D), Color(0xFF4C1D95)]),
      boxShadow: const [BoxShadow(color: Color(0x301D123D), blurRadius: 24, offset: Offset(0, 10))],
    ),
    child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Row(children: [
        Container(width: 42, height: 42,
          decoration: BoxDecoration(color: const Color(0x25FFFFFF), borderRadius: BorderRadius.circular(14)),
          child: const Icon(Icons.auto_awesome_rounded, color: Colors.white)),
        const SizedBox(width: 12),
        const Text('NaqshKaar AI', style: TextStyle(color: Colors.white, fontSize: 23, fontWeight: FontWeight.w900)),
      ]),
      const SizedBox(height: 16),
      const Text('Turn your idea into a design.', style: TextStyle(color: Colors.white, fontSize: 22, fontWeight: FontWeight.w900)),
      const SizedBox(height: 5),
      const Text('اپنا خیال لکھیں، نقشکار اسے ڈیزائن ورک فلو میں بدلنے کے لیے تیار ہے۔',
        textDirection: TextDirection.rtl,
        style: TextStyle(fontFamily: 'JameelNooriNastaleeq', color: Color(0xFFE9D5FF), fontSize: 18)),
    ]),
  );

  Widget _section(String title, String subtitle) => Padding(
    padding: const EdgeInsets.only(bottom: 10, top: 2),
    child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Text(title, style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w900, color: _ink)),
      const SizedBox(height: 2),
      Text(subtitle, style: const TextStyle(fontSize: 11, color: _muted)),
    ]),
  );

  Widget _promptBox() => Container(
    margin: const EdgeInsets.only(bottom: 14),
    decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(20), border: Border.all(color: const Color(0xFFE5E7EB))),
    child: TextField(
      controller: _prompt, minLines: 4, maxLines: 7,
      textDirection: TextDirection.rtl, textAlign: TextAlign.right,
      decoration: InputDecoration(
        hintText: 'مثلاً: مدرسہ کے داخلہ کے لیے خوبصورت پوسٹر...',
        hintTextDirection: TextDirection.rtl,
        prefixIcon: const Icon(Icons.edit_note_rounded, color: _purple),
        border: InputBorder.none, fillColor: Colors.transparent,
        suffixIcon: IconButton(tooltip: 'Clear', onPressed: () => setState(_prompt.clear), icon: const Icon(Icons.close_rounded, color: _muted)),
      ),
    ),
  );

  Widget _presets() => SizedBox(
    height: 76,
    child: ListView.separated(
      scrollDirection: Axis.horizontal, itemCount: _presetItems.length,
      separatorBuilder: (_, __) => const SizedBox(width: 9),
      itemBuilder: (_, i) {
        final item = _presetItems[i];
        return InkWell(
          borderRadius: BorderRadius.circular(17),
          onTap: () => setState(() => _prompt.text = switch (item['title']) {
            'Islamic Poster' => 'ایک خوبصورت اسلامی پوسٹر بنائیں',
            'School Admission' => 'School admission open poster with premium Urdu typography',
            'Naat Invitation' => 'خوبصورت نعتیہ پروگرام دعوت نامہ',
            _ => 'Modern YouTube thumbnail with bold Urdu title',
          }),
          child: Container(width: 145, padding: const EdgeInsets.all(11),
            decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(17), border: Border.all(color: const Color(0xFFE7E4F2))),
            child: Row(children: [
              Text(item['icon']!, style: const TextStyle(fontSize: 22)), const SizedBox(width: 8),
              Expanded(child: Text(item['title']!, maxLines: 2, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800))),
            ]),
          ),
        );
      },
    ),
  );

  Widget _styleChips() => Padding(
    padding: const EdgeInsets.only(bottom: 15),
    child: Wrap(spacing: 8, runSpacing: 8, children: _styles.map((style) {
      final selected = style == _style;
      return ChoiceChip(
        selected: selected, label: Text(style),
        onSelected: (_) => setState(() => _style = style),
        avatar: Icon(style == 'Islamic' ? Icons.mosque_rounded : Icons.auto_awesome_rounded, size: 16, color: selected ? _purple : _muted),
      );
    }).toList()),
  );

  Widget _ratioChips() {
    const ratios = ['1:1', '4:5', '16:9', '9:16'];
    return Padding(
      padding: const EdgeInsets.only(bottom: 18),
      child: Wrap(spacing: 8, children: ratios.map((ratio) {
        final selected = ratio == _ratio;
        return ChoiceChip(selected: selected, label: Text(ratio), onSelected: (_) => setState(() => _ratio = ratio));
      }).toList()),
    );
  }

  Widget _generationProgress() => Container(
    margin: const EdgeInsets.only(top: 12),
    padding: const EdgeInsets.all(13),
    decoration: BoxDecoration(color: const Color(0xFFF1ECFF), borderRadius: BorderRadius.circular(16)),
    child: const Row(children: [
      SizedBox(width: 5),
      Icon(Icons.auto_awesome_rounded, color: _purple, size: 18),
      SizedBox(width: 9),
      Expanded(child: Text('AI artwork create ho raha hai. Please wait…', style: TextStyle(fontSize: 11.5, color: _purple, fontWeight: FontWeight.w700))),
    ]),
  );

  Widget _generateButton() => SizedBox(
    width: double.infinity, height: 56,
    child: FilledButton.icon(
      onPressed: _generating ? null : _generate,
      icon: _generating
        ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
        : const Icon(Icons.auto_awesome_rounded),
      label: Text(_generating ? 'Preparing design…' : 'Generate Design'),
      style: FilledButton.styleFrom(backgroundColor: _purple, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(17))),
    ),
  );

  Widget _resultCard() => Container(
    margin: const EdgeInsets.only(top: 18), padding: const EdgeInsets.all(14),
    decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(22), border: Border.all(color: const Color(0xFFE5E7EB))),
    child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Row(children: [
        const Icon(Icons.check_circle_rounded, color: Color(0xFF16A34A), size: 19),
        const SizedBox(width: 7),
        Text('AI design ready • $_status', style: const TextStyle(fontWeight: FontWeight.w900, color: _ink)),
      ]),
      const SizedBox(height: 12),
      AspectRatio(
        aspectRatio: _ratio == '16:9' ? 16 / 9 : _ratio == '9:16' ? 9 / 16 : _ratio == '4:5' ? 4 / 5 : 1,
        child: Container(
          decoration: BoxDecoration(borderRadius: BorderRadius.circular(17),
            gradient: const LinearGradient(begin: Alignment.topLeft, end: Alignment.bottomRight,
              colors: [Color(0xFF10172D), Color(0xFF292052), Color(0xFF4C1D95)])),
          child: _plan?.imageBytes == null
              ? const Center(child: CircularProgressIndicator())
              : ClipRRect(
                  borderRadius: BorderRadius.circular(17),
                  child: Image.memory(_plan!.imageBytes!, fit: BoxFit.cover),
                ),
        ),
      ),
      const SizedBox(height: 12),
      Row(children: [
        Expanded(child: OutlinedButton.icon(onPressed: _generate, icon: const Icon(Icons.refresh_rounded, size: 18), label: const Text('Regenerate'))),
        const SizedBox(width: 9),
        Expanded(child: FilledButton.icon(onPressed: _useInCanvas, icon: const Icon(Icons.edit_rounded, size: 18), label: const Text('Open in Canvas'), style: FilledButton.styleFrom(backgroundColor: _blue))),
      ]),
    ]),
  );

  void _showInfo() {
    showModalBottomSheet<void>(
      context: context, showDragHandle: true,
      builder: (_) => const SafeArea(child: Padding(
        padding: EdgeInsets.fromLTRB(20, 8, 20, 28),
        child: Column(mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('AI Studio', style: TextStyle(fontSize: 21, fontWeight: FontWeight.w900)),
          SizedBox(height: 8),
          Text('AI is connected through the secure server gateway. Your prompt generates real artwork, then you can open it in the editable NaqshKaar canvas.',
            style: TextStyle(fontSize: 13, height: 1.45, color: _muted)),
        ]),
      )),
    );
  }
}
