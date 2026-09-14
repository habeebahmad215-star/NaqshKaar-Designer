import 'package:flutter/material.dart';
import 'screens/home_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const NaqshKaarDesignerApp());
}

class NaqshKaarDesignerApp extends StatelessWidget {
  const NaqshKaarDesignerApp({super.key});

  @override
  Widget build(BuildContext context) {
    const brand = Color(0xFF7C3AED);
    const ink = Color(0xFF171225);
    const canvasBg = Color(0xFFF7F8FC);

    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'NaqshKaar Designer',
      theme: ThemeData(
        useMaterial3: true,
        scaffoldBackgroundColor: canvasBg,
        colorScheme: ColorScheme.fromSeed(
          seedColor: brand,
          brightness: Brightness.light,
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: Colors.white,
          surfaceTintColor: Colors.transparent,
          elevation: 0,
          scrolledUnderElevation: 0,
          centerTitle: false,
          iconTheme: IconThemeData(color: ink, size: 21),
          actionsIconTheme: IconThemeData(color: ink, size: 21),
          titleTextStyle: TextStyle(
            color: ink,
            fontSize: 16,
            fontWeight: FontWeight.w900,
          ),
        ),
        iconButtonTheme: IconButtonThemeData(
          style: ButtonStyle(
            foregroundColor: const WidgetStatePropertyAll(ink),
            overlayColor: WidgetStatePropertyAll(brand.withValues(alpha: .08)),
            shape: WidgetStatePropertyAll(
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            ),
          ),
        ),
        filledButtonTheme: FilledButtonThemeData(
          style: FilledButton.styleFrom(
            backgroundColor: brand,
            foregroundColor: Colors.white,
            elevation: 0,
            padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
          ),
        ),
        outlinedButtonTheme: OutlinedButtonThemeData(
          style: OutlinedButton.styleFrom(
            foregroundColor: ink,
            side: BorderSide(color: brand.withValues(alpha: .20)),
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 11),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
          ),
        ),
        textButtonTheme: TextButtonThemeData(
          style: TextButton.styleFrom(
            foregroundColor: brand,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          ),
        ),
        popupMenuTheme: PopupMenuThemeData(
          color: Colors.white,
          surfaceTintColor: Colors.transparent,
          elevation: 8,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          textStyle: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: ink),
        ),
        bottomSheetTheme: const BottomSheetThemeData(
          backgroundColor: Colors.white,
          surfaceTintColor: Colors.transparent,
          elevation: 12,
          showDragHandle: true,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
          ),
          clipBehavior: Clip.antiAlias,
        ),
        dialogTheme: DialogThemeData(
          backgroundColor: Colors.white,
          surfaceTintColor: Colors.transparent,
          elevation: 12,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
        ),
        cardTheme: CardThemeData(
          color: Colors.white,
          surfaceTintColor: Colors.transparent,
          elevation: 1,
          margin: EdgeInsets.zero,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: const Color(0xFFF7F8FC),
          isDense: true,
          contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 13),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide: BorderSide.none,
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide: BorderSide.none,
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide: const BorderSide(color: brand, width: 1.4),
          ),
          labelStyle: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700),
        ),
        chipTheme: ChipThemeData(
          backgroundColor: const Color(0xFFF3F0FF),
          selectedColor: brand.withValues(alpha: .14),
          side: BorderSide.none,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          labelStyle: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800),
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        ),
        dividerTheme: const DividerThemeData(
          color: Color(0xFFE9E7F0),
          thickness: 1,
          space: 1,
        ),
        sliderTheme: SliderThemeData(
          activeTrackColor: brand,
          thumbColor: brand,
          overlayColor: brand.withValues(alpha: .10),
          trackHeight: 4,
        ),
        snackBarTheme: SnackBarThemeData(
          behavior: SnackBarBehavior.floating,
          elevation: 8,
          backgroundColor: ink,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
          contentTextStyle: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700),
        ),
      ),
      home: const HomeScreen(),
    );
  }
}
