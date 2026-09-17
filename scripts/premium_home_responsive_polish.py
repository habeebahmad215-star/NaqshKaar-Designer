from pathlib import Path

path = Path("lib/screens/home_screen.dart")
s = path.read_text(encoding="utf-8")

old = """                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 4,
                    mainAxisSpacing: 12,
                    crossAxisSpacing: 10,
                    childAspectRatio: .78,
                  ),"""
new = """                gridDelegate: SliverGridDelegateWithMaxCrossAxisExtent(
                    maxCrossAxisExtent: 150,
                    mainAxisSpacing: 12,
                    crossAxisSpacing: 10,
                    childAspectRatio: .92,
                  ),"""
if old not in s:
    raise SystemExit("Home grid anchor not found")
s = s.replace(old, new, 1)

old = """              padding: const EdgeInsets.fromLTRB(4, 9, 4, 6),
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
if old not in s:
    raise SystemExit("Feature tile anchor not found")
s = s.replace(old, new, 1)

old = """                      fontSize: 10.5,
                      fontWeight: FontWeight.w900,"""
new = """                      fontSize: 10.5,
                      fontWeight: FontWeight.w900,"""
# Keep typography stable; only add a subtle tile minimum height.
old2 = """            child: InkWell(
              onTap: () => _openFeature(title),
              borderRadius: BorderRadius.circular(18),
              child: Container(
                decoration:"""
new2 = """            child: InkWell(
              onTap: () => _openFeature(title),
              borderRadius: BorderRadius.circular(18),
              child: Container(
                constraints: const BoxConstraints(minHeight: 112),
                decoration:"""
if old2 not in s:
    raise SystemExit("Feature container anchor not found")
s = s.replace(old2, new2, 1)

old = """  Widget _primaryButton(String label, VoidCallback onTap) {
    return Material(
      color: Colors.transparent,
      child: InkWell("""
new = """  Widget _primaryButton(String label, VoidCallback onTap) {
    return Material(
      color: Colors.transparent,
      elevation: 0,
      child: InkWell("""
if old in s:
    s = s.replace(old, new, 1)

required = [
    "GridDelegateWithMaxCrossAxisExtent",
    "constraints: const BoxConstraints(minHeight: 112)",
    "Icons.add_rounded",
    "JameelNooriNastaleeq",
]
for item in required:
    if item not in s:
        raise SystemExit(f"Home premium contract missing: {item}")

path.write_text(s, encoding="utf-8")
print("Premium home responsive polish applied and verified.")
