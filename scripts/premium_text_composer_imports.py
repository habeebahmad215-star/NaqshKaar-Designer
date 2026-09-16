from pathlib import Path

W = Path('lib/screens/workspace_screen.dart')
w = W.read_text(encoding='utf-8')
needle = "import 'package:image_picker/image_picker.dart';\n"
import_line = "import 'package:url_launcher/url_launcher.dart';\n"
if import_line not in w:
    if needle not in w:
        raise SystemExit('Expected image_picker import was not found')
    w = w.replace(needle, needle + import_line, 1)
W.write_text(w, encoding='utf-8')
print('Premium text composer imports wired.')
