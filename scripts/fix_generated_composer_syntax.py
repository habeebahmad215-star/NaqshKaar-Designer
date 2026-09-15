from pathlib import Path
import re

path = Path('lib/screens/workspace_screen.dart')
text = path.read_text(encoding='utf-8')

replacement = r'''  Widget _composerFontPanel(String current, ValueChanged<String> onChanged) {
    const fonts = <({String name, String family})>[
      (name: 'Jameel Noori', family: 'JameelNooriNastaleeq'),
      (name: 'Alvi Nastaleeq', family: 'AlviNastaleeq'),
      (name: 'Mehr Nastaliq', family: 'MehrNastaliq'),
      (name: 'Gulzar', family: 'Gulzar'),
      (name: 'Noto Nastaliq', family: 'NotoNastaliqUrdu'),
      (name: 'Al Majeed', family: 'AlMajeedQuranic'),
      (name: 'Bombay Black', family: 'BombayBlack'),
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Padding(
          padding: EdgeInsets.fromLTRB(4, 0, 4, 8),
          child: Text(
            'Font Family',
            style: TextStyle(fontSize: 12, fontWeight: FontWeight.w900, color: Colors.black54),
          ),
        ),
        SizedBox(
          height: 88,
          child: ListView.separated(
            scrollDirection: Axis.horizontal,
            itemCount: fonts.length,
            separatorBuilder: (_, __) => const SizedBox(width: 8),
            itemBuilder: (context, index) {
              final font = fonts[index];
              final active = current == font.family;
              return InkWell(
                onTap: () => onChanged(font.family),
                borderRadius: BorderRadius.circular(16),
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 160),
                  width: 116,
                  padding: const EdgeInsets.all(9),
                  decoration: BoxDecoration(
                    color: active ? _primary.withValues(alpha: .08) : Colors.white,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(
                      color: active ? _primary : const Color(0x16000000),
                      width: active ? 1.7 : 1,
                    ),
                  ),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Expanded(
                        child: FittedBox(
                          fit: BoxFit.scaleDown,
                          child: Text(
                            'اردو',
                            style: TextStyle(
                              fontFamily: font.family,
                              fontSize: 30,
                              color: _primary,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        font.name,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w800),
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
        ),
      ],
    );
  }

'''

new_text, count = re.subn(
    r"  Widget _composerFontPanel\(String current, ValueChanged<String> onChanged\) \{.*?\n  Widget _composerSizePanel",
    replacement + "  Widget _composerSizePanel",
    text,
    count=1,
    flags=re.S,
)
if count != 1:
    raise SystemExit('Could not locate generated composer font panel.')

path.write_text(new_text, encoding='utf-8')
print('Fixed generated composer font panel syntax.')
