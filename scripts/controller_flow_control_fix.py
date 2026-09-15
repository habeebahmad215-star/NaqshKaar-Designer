from pathlib import Path

path = Path('lib/state/workspace_controller.dart')
text = path.read_text(encoding='utf-8')

# Image Studio historically emitted these two guards on one line. Keep the
# fix explicit and idempotent so it cannot accidentally rewrite unrelated Dart.
replacements = {
    'if (x != null) e.imageOffsetX = x.clamp(-1, 1).toDouble();':
        'if (x != null) {\n      e.imageOffsetX = x.clamp(-1, 1).toDouble();\n    }',
    'if (y != null) e.imageOffsetY = y.clamp(-1, 1).toDouble();':
        'if (y != null) {\n      e.imageOffsetY = y.clamp(-1, 1).toDouble();\n    }',
}

for old, new in replacements.items():
    text = text.replace(old, new)

if 'if (x != null) e.imageOffsetX =' in text or 'if (y != null) e.imageOffsetY =' in text:
    raise SystemExit('Controller flow-control fix verification failed.')

path.write_text(text, encoding='utf-8')
print('Controller inline Image Studio flow statements normalized successfully.')
