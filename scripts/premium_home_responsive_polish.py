from pathlib import Path
import re

path = Path("lib/screens/home_screen.dart")
s = path.read_text(encoding="utf-8")

# The Home screen is produced by several ordered transformation passes.
# Never depend on one exact whitespace/padding snapshot; normalize the final
# feature grid/tile structure idempotently.
if "maxCrossAxisExtent: 150" not in s:
    raise SystemExit("Home responsive grid anchor not found")
s = re.sub(
    r"gridDelegate:\s*(?:const\s+)?SliverGridDelegateWithMaxCrossAxisExtent\(.*?\),",
    """gridDelegate: SliverGridDelegateWithMaxCrossAxisExtent(
                    maxCrossAxisExtent: 150,
                    mainAxisSpacing: 12,
                    crossAxisSpacing: 10,
                    childAspectRatio: .92,
                  )""",
    s,
    count=1,
    flags=re.S,
)

# Scope tile normalization to _featureTile so unrelated Containers are untouched.
start = s.find("Widget _featureTile(")
end = s.find("Widget _recentProjects(", start)
if start < 0 or end < 0:
    raise SystemExit("Feature tile method not found")
head, body, tail = s[:start], s[start:end], s[end:]

body = re.sub(
    r"padding:\s*const EdgeInsets\.fromLTRB\([^\n]+\),",
    "padding: const EdgeInsets.fromLTRB(5, 10, 5, 7),",
    body,
    count=1,
)
body = re.sub(
    r"child: Container\(\s*width:\s*48,\s*height:\s*48,",
    """child: Container(
                    width: 46,
                    height: 46,""",
    body,
    count=1,
    flags=re.S,
)
if "constraints: const BoxConstraints(minHeight: 112)" not in body:
    body = body.replace(
        """child: Container(
                decoration:""",
        """child: Container(
                constraints: const BoxConstraints(minHeight: 112),
                decoration:""",
        1,
    )

if "constraints: const BoxConstraints(minHeight: 112)" not in body:
    raise SystemExit("Feature tile minimum-height anchor not found")

s = head + body + tail

required = [
    "maxCrossAxisExtent: 150",
    "constraints: const BoxConstraints(minHeight: 112)",
    "Icons.add_rounded",
    "JameelNooriNastaleeq",
]
for item in required:
    if item not in s:
        raise SystemExit(f"Home premium contract missing: {item}")

path.write_text(s, encoding="utf-8")
print("Premium home responsive polish normalized and verified.")
