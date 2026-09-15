from pathlib import Path

path = Path('lib/services/export_service.dart')
text = path.read_text()

if "import 'dart:math' as math;" not in text:
    text = text.replace("import 'dart:ui' as ui;", "import 'dart:ui' as ui;\nimport 'dart:math' as math;", 1)

text = text.replace(
    "mathMin(requestedRatio, mathSqrt(_maxRasterPixels / (logicalWidth * logicalHeight)))",
    "math.sqrt(_maxRasterPixels / (logicalWidth * logicalHeight)) < requestedRatio\n            ? math.sqrt(_maxRasterPixels / (logicalWidth * logicalHeight))\n            : requestedRatio",
)
text = text.replace("  double mathMin(double a, double b) => a < b ? a : b;\n  double mathSqrt(double value) => value <= 0 ? 0 : value.sqrt();\n\n", "")

path.write_text(text)
print('Export raster safety implementation normalized successfully')
