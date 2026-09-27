#!/usr/bin/env bash
set -euo pipefail

FLUTTER_DIR="${HOME}/.flutter-sdk"

if [ ! -x "${FLUTTER_DIR}/bin/flutter" ]; then
  echo "Installing Flutter SDK..."
  rm -rf "${FLUTTER_DIR}"
  git clone --depth 1 --branch stable https://github.com/flutter/flutter.git "${FLUTTER_DIR}"
fi

export PATH="${FLUTTER_DIR}/bin:${PATH}"

flutter config --enable-web
flutter --version

echo "Configuring Flutter Web..."
flutter create --platforms=web .

echo "Downloading bundled Urdu fonts..."
mkdir -p assets/fonts
curl -fL --retry 3 -o assets/fonts/Gulzar-Regular.ttf https://raw.githubusercontent.com/googlefonts/Gulzar/main/fonts/ttf/Gulzar-Regular.ttf
curl -fL --retry 3 -o assets/fonts/NotoNastaliqUrdu-Regular.ttf https://raw.githubusercontent.com/harfbuzz/harfbuzz-monster-fonts/main/NotoNastaliqUrdu-Regular.ttf
curl -fL --retry 3 -o assets/fonts/MehrNastaliq.ttf https://raw.githubusercontent.com/abbassiddiqi/mehr/master/mehr.ttf
curl -fL --retry 3 -o assets/fonts/AlviNastaleeq.ttf https://raw.githubusercontent.com/imrofayel/UrduFonts/master/fonts/AlviNastaleeq.ttf
curl -fL --retry 3 -o assets/fonts/JameelNooriNastaleeq.ttf "https://raw.githubusercontent.com/abid-mujtaba/ttf-jameel-noori-nastaleeq/master/Jameel%20Noori%20Nastaleeq.ttf"
curl -fL --retry 3 -o assets/fonts/AlMajeedQuranic.ttf https://fontly-virid.vercel.app/fonts/ttf/al-majeed-quranic-font-shiped.ttf
curl -fL --retry 3 -o assets/fonts/BombayBlack.ttf https://www.urdufont.org/download.php?id=737645
for font in assets/fonts/*.ttf; do
  test -s "$font"
done

echo "Preparing generated source..."
python3 -m py_compile scripts/*.py
rm -rf test
sed -i 's/Icons\.rotate_0_degrees_ccw_rounded/Icons.rotate_left_rounded/g' lib/screens/workspace_screen.dart

python3 scripts/font_catalog_upgrade.py
python3 scripts/fix_generated_composer_syntax.py
python3 scripts/final_toolbar_polish.py
python3 scripts/canvas_interaction_upgrade.py
python3 scripts/image_studio_upgrade.py
python3 scripts/advanced_layers_upgrade.py
python3 scripts/layers_studio_build_fix.py
python3 scripts/typography_studio_upgrade.py
python3 scripts/reliability_upgrade.py
python3 scripts/export_safety_upgrade.py
python3 scripts/remaining_tools_upgrade.py
python3 scripts/premium_workspace_ui_upgrade.py
python3 scripts/fix_premium_workspace_ui.py
python3 scripts/premium_text_composer_upgrade.py
python3 scripts/premium_text_composer_imports.py
python3 scripts/fix_premium_canvas_size.py
python3 scripts/paper_resize_and_selection_upgrade.py
python3 scripts/controller_flow_control_fix.py
python3 scripts/premium_editor_catalog_upgrade.py
python3 scripts/premium_editor_catalog_repair.py
python3 scripts/deep_screenshot_polish.py
python3 scripts/deep_functional_repair.py
python3 scripts/home_compact_polish.py
python3 scripts/final_catalog_render_repair.py
python3 scripts/final_runtime_catalog_visibility_repair.py
python3 scripts/pre_editor_ux_layer_label.py
python3 scripts/final_editor_ux_repair_v2.py
python3 scripts/final_live_preview_and_selection_recovery.py
python3 scripts/continuous_edit_checkpoint_hardening.py
python3 scripts/final_editor_ux_safety.py
python3 scripts/continuous_edit_checkpoint_hardening.py
python3 scripts/final_acceptance_polish.py

python3 - <<'PY'
from pathlib import Path
path = Path('analysis_options.yaml')
text = path.read_text(encoding='utf-8')
rule = 'curly_braces_in_flow_control_structures: false'
if rule not in text:
    marker = 'linter:\n'
    rules_marker = '  rules:\n'
    if marker not in text or rules_marker not in text:
        raise SystemExit('Expected Flutter-generated linter/rules block was not found')
    text = text.replace(rules_marker, rules_marker + '    ' + rule + '\n', 1)
    path.write_text(text, encoding='utf-8')
PY

python3 - <<'PY'
from pathlib import Path
path = Path('lib/widgets/design_canvas.dart')
lines = path.read_text(encoding='utf-8').splitlines(keepends=True)
kept = [line for line in lines if 'textHeightBehavior:' not in line]
path.write_text(''.join(kept), encoding='utf-8')
PY

flutter pub get
dart fix --apply
dart format lib
flutter analyze
flutter build web --release

test -f build/web/index.html
echo "Flutter web build completed successfully."
