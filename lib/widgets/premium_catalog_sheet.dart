import 'package:flutter/material.dart';
import 'premium_catalogs.dart';

class PremiumSpecialText {
  static String value(int index) => PremiumShapeCatalog.specialText(index);
}

class PremiumCatalogSheet extends StatefulWidget {
  final ValueChanged<int> onShape;
  final ValueChanged<int> onBorder;
  final ValueChanged<int> onSpecialText;
  final int initialTab;

  const PremiumCatalogSheet({
    super.key,
    required this.onShape,
    required this.onBorder,
    required this.onSpecialText,
    this.initialTab = 0,
  });

  @override
  State<PremiumCatalogSheet> createState() => _PremiumCatalogSheetState();
}

class _PremiumCatalogSheetState extends State<PremiumCatalogSheet>
    with SingleTickerProviderStateMixin {
  late final TabController _tabs = TabController(
    length: 3,
    vsync: this,
    initialIndex: widget.initialTab.clamp(0, 2),
  );

  @override
  void dispose() {
    _tabs.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(16, 8, 16, 18),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Row(
              children: [
                Container(
                  width: 42,
                  height: 42,
                  decoration: BoxDecoration(
                    color: const Color(0xFF6D28D9).withValues(alpha: .1),
                    borderRadius: BorderRadius.circular(14),
                  ),
                  child: const Icon(Icons.auto_awesome_rounded,
                      color: Color(0xFF6D28D9)),
                ),
                const SizedBox(width: 12),
                const Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Premium Library',
                          style: TextStyle(
                              fontSize: 21, fontWeight: FontWeight.w900)),
                      Text('100+ ready-made designs',
                          style:
                              TextStyle(color: Colors.black54, fontSize: 12)),
                    ],
                  ),
                ),
                IconButton(
                    onPressed: () => Navigator.pop(context),
                    icon: const Icon(Icons.close_rounded)),
              ],
            ),
            const SizedBox(height: 8),
            TabBar(
              controller: _tabs,
              tabs: const [
                Tab(text: 'Shapes 100+'),
                Tab(text: 'Borders 100+'),
                Tab(text: 'Special Text 100+'),
              ],
            ),
            const SizedBox(height: 8),
            SizedBox(
              height: MediaQuery.sizeOf(context).height * .62,
              child: TabBarView(
                controller: _tabs,
                children: [
                  _grid(PremiumShapeCatalog.shapeNames, widget.onShape),
                  _grid(PremiumShapeCatalog.borderNames, widget.onBorder,
                      border: true),
                  _textGrid(),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _grid(List<String> names, ValueChanged<int> tap,
      {bool border = false}) {
    return GridView.builder(
      padding: const EdgeInsets.only(bottom: 12),
      itemCount: names.length,
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 3,
        mainAxisSpacing: 10,
        crossAxisSpacing: 10,
        childAspectRatio: .88,
      ),
      itemBuilder: (context, i) {
        return Material(
          color: Colors.white,
          borderRadius: BorderRadius.circular(17),
          child: InkWell(
            borderRadius: BorderRadius.circular(17),
            onTap: () => tap(i),
            child: Padding(
              padding: const EdgeInsets.all(7),
              child: Column(
                children: [
                  Expanded(
                    child: Container(
                      width: double.infinity,
                      decoration: BoxDecoration(
                        color: const Color(0xFFF7F5FC),
                        borderRadius: BorderRadius.circular(13),
                      ),
                      child: CustomPaint(
                        painter: CatalogShapePainter(
                          type: i,
                          fill: const Color(0xFF7C3AED),
                          stroke: const Color(0xFF6D28D9),
                          strokeWidth: 3,
                          border: border,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 5),
                  Text(
                    '${i + 1}. ${names[i]}',
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    textAlign: TextAlign.center,
                    style: const TextStyle(
                        fontSize: 9, fontWeight: FontWeight.w800),
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _textGrid() {
    return GridView.builder(
      padding: const EdgeInsets.only(bottom: 12),
      itemCount: PremiumShapeCatalog.specialTextNames.length,
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        mainAxisSpacing: 10,
        crossAxisSpacing: 10,
        childAspectRatio: 1.45,
      ),
      itemBuilder: (context, i) {
        return Material(
          color: Colors.white,
          borderRadius: BorderRadius.circular(17),
          child: InkWell(
            borderRadius: BorderRadius.circular(17),
            onTap: () => widget.onSpecialText(i),
            child: Padding(
              padding: const EdgeInsets.all(10),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    PremiumShapeCatalog.specialText(i),
                    textAlign: TextAlign.center,
                    textDirection: TextDirection.rtl,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      fontFamily: 'JameelNooriNastaleeq',
                      fontSize: 20,
                      color: Color(0xFF6D28D9),
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 3),
                  Text(
                    '${i + 1}. ${PremiumShapeCatalog.specialTextNames[i]}',
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                        fontSize: 9, fontWeight: FontWeight.w800),
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }
}
