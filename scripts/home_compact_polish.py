from pathlib import Path
import re

# Home is normalized in ONE deterministic pass. Earlier pipeline passes may
# leave either the original fixed-count grid or the intermediate 176px grid.
# Accept both states, then own the final responsive phone/wide layout here.
p = Path('lib/screens/home_screen.dart')
s = p.read_text(encoding='utf-8')

grid = re.compile(
    r'(?:const\s+)?SliverGridDelegateWith(?:FixedCrossAxisCount|MaxCrossAxisExtent)\(.*?\)',
    re.S,
)
match = grid.search(s)
if not match:
    raise SystemExit('Home feature grid was not found')

final_grid = '''SliverGridDelegateWithMaxCrossAxisExtent(
                    maxCrossAxisExtent: 150,
                    mainAxisSpacing: 10,
                    crossAxisSpacing: 8,
                    childAspectRatio: 1.15,
                  )'''
s = s[:match.start()] + final_grid + s[match.end():]

# Keep the Home vertical rhythm compact and idempotent.
s = re.sub(
    r'const SliverToBoxAdapter\(child: SizedBox\(height:\s*(?:88|132|104),\)\)',
    'const SliverToBoxAdapter(child: SizedBox(height: 104))',
    s,
    count=1,
)
s = re.sub(r'height:\s*(?:190|210|198),', 'height: 198,', s, count=1)

# Own the feature-tile presentation here instead of chaining another script
# that expects a particular intermediate whitespace snapshot.
start = s.find('Widget _featureTile(')
end = s.find('Widget _recentProjects(', start)
if start < 0 or end < 0:
    raise SystemExit('Home feature tile method was not found')

head, body, tail = s[:start], s[start:end], s[end:]
body = re.sub(
    r'padding:\s*const EdgeInsets\.fromLTRB\([^\n]+\),',
    'padding: const EdgeInsets.fromLTRB(5, 10, 5, 7),',
    body,
    count=1,
)
body = re.sub(
    r'width:\s*48,\s*\n\s*height:\s*48,',
    'width: 46,\n                    height: 46,',
    body,
    count=1,
)
body = re.sub(
    r'(child: Container\(\n)(\s*decoration: BoxDecoration\()',
    r'\1                constraints: const BoxConstraints(minHeight: 112),\n\2',
    body,
    count=1,
)
body = re.sub(
    r'maxLines:\s*1,\s*\n\s*overflow:\s*TextOverflow\.ellipsis,',
    'maxLines: 2,\n                    softWrap: true,\n                    overflow: TextOverflow.clip,',
    body,
)
s = head + body + tail

required = [
    'maxCrossAxisExtent: 150',
    'constraints: const BoxConstraints(minHeight: 112)',
    "Icons.add_rounded",
    "JameelNooriNastaleeq",
]
for item in required:
    if item not in s:
        raise SystemExit(f'Home compact contract missing: {item}')

p.write_text(s, encoding='utf-8')
print('Home normalized in one deterministic pass: responsive grid, compact rhythm, and premium feature tiles verified.')
