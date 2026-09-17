from pathlib import Path

path = Path("lib/screens/home_screen.dart")
s = path.read_text(encoding="utf-8")

# This pass runs after deep_functional_repair.py and home_compact_polish.py.
# Target the actual post-pipeline form so the polish is deterministic/idempotent.
old = """                gridDelegate: const SliverGridDelegateWithMaxCrossAxisExtent(
                    maxCrossAxisExtent: 150,
                    mainAxisSpacing: 10,
                    crossAxisSpacing: 8,
                    childAspectRatio: 1.15,
                  ),"""
new = """                gridDelegate: SliverGridDelegateWithMaxCrossAxisExtent(
                    maxCrossAxisExtent: 150,
                    mainAxisSpacing: 12,
                    crossAxisSpacing: 10,
                    childAspectRatio: .92,
                  ),"""
if old in s:
    s = s.replace(old, new, 1)
elif """maxCrossAxisExtent: 150""" not in s:
    raise SystemExit("Home responsive grid anchor not found")

old = """              padding: const EdgeInsets.fromLTRB(7, 10, 7, 8),
              child: Column(
                children: [
                  Container(
                    width: 48,
                    height: 48,"""
new = """              padding: const EdgeInsets.fromLTRB(5, 10, 5, 7),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Container(
                    width: 46,
                    height: 46,"""
if old in s:
    s = s.replace(old, new, 1)
elif "constraints: const BoxConstraints(minHeight: 112)" not in s:
    raise SystemExit("Feature tile anchor not found")

old = """            child: InkWell(
              onTap: () => _openFeature(title),
              borderRadius: BorderRadius.circular(18),
              child: Container(
                decoration:"""
new = """            child: InkWell(
              onTap: () => _openFeature(title),
              borderRadius: BorderRadius.circular(18),
              child: Container(
                constraints: const BoxConstraints(minHeight: 112),
                decoration:"""
if old in s:
    s = s.replace(old, new, 1)

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
print("Premium home responsive polish applied and verified.")
