from pathlib import Path

# The responsive pass previously used a 176px max tile width with a near-square
# ratio. On normal phones that resolves to only 2 columns, making the 12 studio
# actions unnecessarily tall. Keep the grid responsive, but make the action
# tiles compact: 3 columns on typical phones and 4 on wider screens.
p = Path('lib/screens/home_screen.dart')
s = p.read_text(encoding='utf-8')
old = """const SliverGridDelegateWithMaxCrossAxisExtent(\n                    maxCrossAxisExtent: 176,\n                    mainAxisSpacing: 12,\n                    crossAxisSpacing: 10,\n                    childAspectRatio: .96,\n                  )"""
new = """const SliverGridDelegateWithMaxCrossAxisExtent(\n                    maxCrossAxisExtent: 150,\n                    mainAxisSpacing: 10,\n                    crossAxisSpacing: 8,\n                    childAspectRatio: 1.15,\n                  )"""
if old not in s:
    raise SystemExit('Expected responsive home grid pattern was not found')
s = s.replace(old, new, 1)

# Give the feature section a little less vertical overhead while preserving the
# premium hero, recent-projects and bottom-navigation breathing room.
s = s.replace("const SliverToBoxAdapter(child: SizedBox(height: 132)),", "const SliverToBoxAdapter(child: SizedBox(height: 104)),", 1)
s = s.replace("height: 210,", "height: 198,", 1)

p.write_text(s, encoding='utf-8')
print('Compact premium home grid applied: 3-column phone layout, 4-column wider layout.')
