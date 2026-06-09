import 'package:app1/core/themes/app_colors.dart';
import 'package:flutter/material.dart';

/// Color tokens used by the warning screen.
class WarningColors {
  static const Color warningRed = AppColors.warningRed;
  static const Color warningBackground = AppColors.warningBackground;
  static const Color warningIconBackground = AppColors.warningIconBackground;
  static const Color darkText = AppColors.careenaDark;
  static const Color teal = AppColors.careenaTeal;
}

/// Text styles shared across warning widgets.
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

  static TextStyle bodyFor(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return TextStyle(
      color: isDarkMode
          ? Theme.of(context).colorScheme.onSurfaceVariant
          : WarningColors.darkText,
      fontSize: 13,
      height: 1.35,
    );
  }

  static TextStyle captionFor(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return TextStyle(
      color: isDarkMode
          ? Theme.of(context).colorScheme.onSurfaceVariant
          : WarningColors.darkText,
      fontSize: 12,
      height: 1.35,
    );
  }

  static TextStyle titleFor(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return TextStyle(
      color: isDarkMode
          ? Theme.of(context).colorScheme.onSurface
          : WarningColors.darkText,
      fontWeight: FontWeight.bold,
    );
  }
}

/// Reusable decorations for warning cards and information boxes.
class WarningDecorations {
  static BoxDecoration emergencyCard(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return BoxDecoration(
      color: isDarkMode
          ? AppColors.warningEmergencyBackgroundDark
          : WarningColors.warningBackground,
      borderRadius: BorderRadius.circular(14),
      border: Border.all(
        color: isDarkMode
            ? WarningColors.warningRed.withValues(alpha: 0.65)
            : WarningColors.warningRed,
        width: 1.4,
      ),
      boxShadow: [
        BoxShadow(
          color: Colors.black.withValues(alpha: isDarkMode ? 0.18 : 0.05),
          blurRadius: 10,
          offset: const Offset(0, 4),
        ),
      ],
    );
  }

  static BoxDecoration reasonBox(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return BoxDecoration(
      color: isDarkMode
          ? AppColors.warningReasonBackgroundDark
          : Colors.white.withValues(alpha: 0.72),
      borderRadius: BorderRadius.circular(10),
      border: Border.all(
        color: WarningColors.warningRed.withValues(
          alpha: isDarkMode ? 0.35 : 0.18,
        ),
      ),
    );
  }

  static BoxDecoration infoBox(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return BoxDecoration(
      color: isDarkMode ? colorScheme.surface : Colors.white,
      borderRadius: BorderRadius.circular(14),
      border: Border.all(
        color: isDarkMode ? colorScheme.outlineVariant : Colors.grey.shade200,
      ),
      boxShadow: [
        BoxShadow(
          color: Colors.black.withValues(alpha: isDarkMode ? 0.16 : 0.03),
          blurRadius: 8,
          offset: const Offset(0, 3),
        ),
      ],
    );
  }
}
