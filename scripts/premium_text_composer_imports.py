from pathlib import Path

W = Path('lib/screens/workspace_screen.dart')
w = W.read_text(encoding='utf-8')

# The composer needs Flutter clipboard APIs; remove the now-unused typed_data import.
w = w.replace("import 'dart:typed_data';\n", '')
needle = "import 'package:image_picker/image_picker.dart';\n"
imports = [
    "import 'package:flutter/services.dart';\n",
    "import 'package:url_launcher/url_launcher.dart';\n",
]
if needle not in w:
    raise SystemExit('Expected image_picker import was not found')
for import_line in imports:
    if import_line not in w:
        w = w.replace(needle, needle + import_line, 1)
W.write_text(w, encoding='utf-8')
print('Premium text composer imports normalized.')
