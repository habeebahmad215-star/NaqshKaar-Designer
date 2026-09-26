import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../services/ai_service.dart';

class AiStudioSheet extends StatefulWidget {
  final ValueChanged<String> onWriteResult;
  final ValueChanged<Uint8List> onImageResult;

  const AiStudioSheet({
    super.key,
    required this.onWriteResult,
    required this.onImageResult,
  });

  @override
  State<AiStudioSheet> createState() => _AiStudioSheetState();
}

class _AiStudioSheetState extends State<AiStudioSheet> {
  final AiService _ai = AiService();
  final ImagePicker _picker = ImagePicker();
  final TextEditingController _prompt = TextEditingController();
  String _language = 'Urdu';
  String _style = 'Premium';
  bool _busy = false;
  Uint8List? _sourceImage;

  @override
  void dispose() {
    _prompt.dispose();
    _ai.dispose();
    super.dispose();
  }

  Future<void> _run(Future<void> Function() action) async {
    if (_busy) return;
    setState(() => _busy = true);
    try {
      await action();
    } catch (error) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(error.toString().replaceFirst('Exception: ', ''))),
      );
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _pickSource() async {
    final picked = await _picker.pickImage(source: ImageSource.gallery);
    if (picked == null) return;
    setState(() => _sourceImage = null);
    final bytes = await picked.readAsBytes();
    if (mounted) setState(() => _sourceImage = bytes);
  }

  Future<void> _write() async {
    final prompt = _prompt.text.trim();
    if (prompt.isEmpty) return;
    await _run(() async {
      final result = await _ai.write(prompt, language: _language);
      if (!mounted) return;
      widget.onWriteResult(result);
      Navigator.pop(context);
    });
  }

  Future<void> _image() async {
    final prompt = _prompt.text.trim();
    if (prompt.isEmpty) return;
    await _run(() async {
      final bytes = await _ai.generateImage(prompt, style: _style);
      if (!mounted) return;
      widget.onImageResult(bytes);
      Navigator.pop(context);
    });
  }

  Future<void> _transform(
    Future<Uint8List> Function(Uint8List) operation,
    String label,
  ) async {
    final source = _sourceImage;
    if (source == null) {
      await _pickSource();
      return;
    }
    await _run(() async {
      final bytes = await operation(source);
      if (!mounted) return;
      widget.onImageResult(bytes);
      Navigator.pop(context);
    });
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(18, 8, 18, 22),
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('AI Studio', style: TextStyle(fontSize: 23, fontWeight: FontWeight.w900)),
              const SizedBox(height: 3),
              Text(
                _ai.configured ? 'AI Write • Image • Magic tools' : aiConfigurationHint(),
                style: const TextStyle(fontSize: 11, color: Colors.black54),
              ),
              const SizedBox(height: 14),
              TextField(
                controller: _prompt,
                minLines: 2,
                maxLines: 5,
                textDirection: TextDirection.rtl,
                decoration: InputDecoration(
                  labelText: 'Describe what you want',
                  hintText: 'مثلاً: مدرسہ کے سالانہ پروگرام کے لیے خوبصورت اعلان لکھیں',
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(16)),
                ),
              ),
              const SizedBox(height: 10),
              Row(
                children: [
                  Expanded(
                    child: DropdownButtonFormField<String>(
                      initialValue: _language,
                      decoration: const InputDecoration(labelText: 'Language'),
                      items: const [
                        DropdownMenuItem(value: 'Urdu', child: Text('Urdu')),
                        DropdownMenuItem(value: 'Hindi', child: Text('Hindi')),
                        DropdownMenuItem(value: 'English', child: Text('English')),
                        DropdownMenuItem(value: 'Arabic', child: Text('Arabic')),
                      ],
                      onChanged: (v) => setState(() => _language = v ?? 'Urdu'),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: DropdownButtonFormField<String>(
                      initialValue: _style,
                      decoration: const InputDecoration(labelText: 'Image style'),
                      items: const [
                        DropdownMenuItem(value: 'Premium', child: Text('Premium')),
                        DropdownMenuItem(value: 'Minimal', child: Text('Minimal')),
                        DropdownMenuItem(value: 'Islamic', child: Text('Islamic')),
                        DropdownMenuItem(value: 'Realistic', child: Text('Realistic')),
                      ],
                      onChanged: (v) => setState(() => _style = v ?? 'Premium'),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 14),
              Wrap(
                spacing: 9,
                runSpacing: 9,
                children: [
                  _action(Icons.edit_note_rounded, 'AI Write', _write),
                  _action(Icons.image_rounded, 'AI Image', _image),
                  _action(Icons.auto_fix_high_rounded, 'Magic Remove', () => _transform(_ai.magicRemove, 'Magic Remove')),
                  _action(Icons.person_remove_rounded, 'BG Remove', () => _transform(_ai.removeBackground, 'BG Remove')),
                  _action(Icons.high_quality_rounded, 'AI Enhance', () => _transform(_ai.enhance, 'AI Enhance')),
                  _action(Icons.photo_filter_rounded, 'AI Edit', () => _transform((bytes) => _ai.magicRemove(bytes, instruction: _prompt.text), 'AI Edit')),
                ],
              ),
              if (_sourceImage != null) ...[
                const SizedBox(height: 12),
                ClipRRect(
                  borderRadius: BorderRadius.circular(14),
                  child: Image.memory(_sourceImage!, height: 110, width: double.infinity, fit: BoxFit.contain),
                ),
              ],
              if (_busy)
                const Padding(
                  padding: EdgeInsets.only(top: 14),
                  child: LinearProgressIndicator(minHeight: 3),
                ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _action(IconData icon, String label, VoidCallback onTap) {
    return FilledButton.tonalIcon(
      onPressed: _busy ? null : onTap,
      icon: Icon(icon, size: 19),
      label: Text(label),
    );
  }
}
