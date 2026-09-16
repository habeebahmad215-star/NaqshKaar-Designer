from pathlib import Path

W = Path('lib/screens/workspace_screen.dart')
w = W.read_text(encoding='utf-8')

# ProjectModel stores the background on the current DesignPage.
w = w.replace('controller.project.backgroundColorValue', 'controller.page.background.toARGB32()')

# The first UI pass briefly wrapped two Wrap widgets in an extra scroll view.
# Keep the original Wrap layout; the sheet itself remains bounded by its bottom-sheet viewport.
w = w.replace('child: SingleChildScrollView(child: Wrap(', 'child: Wrap(')

# Balance the extra close introduced for the More sheet by the first pass.
start = w.find('  Future<void> _moreSheet()')
end = w.find('\n  Future<void> _pagesSheet()', start)
if start >= 0 and end > start:
    section = w[start:end]
    section = section.replace('            ],\n          )),\n        );', '            ],\n          ),\n        );')
    w = w[:start] + section + w[end:]

W.write_text(w, encoding='utf-8')
print('Premium workspace UI transformation corrected.')
