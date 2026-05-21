import 'package:flutter/material.dart';

class WarningColors {
  static const Color warningRed = Color(0xFFFF3045);
  static const Color warningBackground = Color(0xFFFFF1F3);
  static const Color warningIconBackground = Color(0xFFFFDCE1);
  static const Color darkText = Color(0xFF2C5358);
  static const Color teal = Color(0xFF26A69A);
}

class WarningTextStyles {
  static const TextStyle body = TextStyle(
    color: WarningColors.darkText,
    fontSize: 13,
    height: 1.35,
  );

  static const TextStyle highlight = TextStyle(
    color: WarningColors.warningRed,
    fontWeight: FontWeight.bold,
  );

  static const TextStyle caption = TextStyle(
    color: WarningColors.darkText,
    fontSize: 12,
    height: 1.35,
  );
}

class WarningDecorations {
  static final BoxDecoration emergencyCard = BoxDecoration(
    color: WarningColors.warningBackground,
    borderRadius: BorderRadius.circular(14),
    border: Border.all(color: WarningColors.warningRed, width: 1.4),
    boxShadow: [
      BoxShadow(
        color: Colors.black.withValues(alpha: 0.05),
        blurRadius: 10,
        offset: const Offset(0, 4),
      ),
    ],
  );

  static final BoxDecoration reasonBox = BoxDecoration(
    color: Colors.white.withValues(alpha: 0.72),
    borderRadius: BorderRadius.circular(10),
    border: Border.all(color: WarningColors.warningRed.withValues(alpha: 0.18)),
  );

  static final BoxDecoration infoBox = BoxDecoration(
    color: Colors.white,
    borderRadius: BorderRadius.circular(14),
    border: Border.all(color: Colors.grey.shade200),
    boxShadow: [
      BoxShadow(
        color: Colors.black.withValues(alpha: 0.03),
        blurRadius: 8,
        offset: const Offset(0, 3),
      ),
    ],
  );
}
