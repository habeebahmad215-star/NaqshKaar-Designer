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
flutter pub get
flutter build web --release

test -f build/web/index.html
echo "Flutter web build completed successfully."
