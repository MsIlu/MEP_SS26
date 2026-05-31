import 'package:flutter/material.dart';

/// Shared color tokens used by chat and home UI components
/// (for consistent color usage across the entire application).
class AppColors {
  AppColors._();

  // Brand colors
  static const Color primary = Color(0xFF4A90E2);
  static const Color accent = Color(0xFF2ECC71);

  // Light mode
  static const Color lightBackground = Color(0xFFF2F5FA);
  static const Color lightCard = Colors.white;
  static const Color lightTextPrimary = Color(0xFF1F2D3D);
  static const Color lightTextSecondary = Colors.grey;

  // Darkmode
  static const Color darkBackground = Color(0xFF101820);
  static const Color darkCard = Color(0xFF1B2733);
  static const Color darkTextPrimary = Color(0xFFF2F5FA);
  static const Color darkTextSecondary = Color(0xFFB0BEC5);

  // Legacy aliases while migrating widgets to Theme.of(context).
  static const Color background = lightBackground;
  static const Color card = lightCard;
  static const Color textPrimary = lightTextPrimary;
  static const Color textSecondary = lightTextSecondary;

  // Existing Careena colors
  static const Color upperBarColor = Color(0xFF1565C0);
  static const Color lowerBarColor = Color(0xFFE0E0E0);

  static const Color careenaBackground = Color(0xFFDDF1F1);
  static const Color careenaPrimary = Color(0xFF37AEB5);
  static const Color careenaTeal = Color(0xFF26A69A);
  static const Color careenaDark = Color(0xFF2C5358);
  static const Color careenaTitle = Color(0xFF244C52);
  static const Color careenaBody = Color(0xFF385D63);
  static const Color careenaMuted = Color(0xFF5F7478);
  static const Color careenaBorder = Color(0xFFE1E9EA);
  static const Color careenaBubbleBackground = Color(0xFFE7F5F3);
  static const Color careenaInfoBorder = Color(0xFFB8E4E8);
  static const Color careenaSoftAccent = Color(0xFFB9E7E7);
  static const Color careenaNoteBackground = Color(0xFFEAF8F8);
  static const Color careenaBrand = Color(0xFF43B8BE);
  static const Color onboardingButtonText = Color(0xFF1D2B34);
  static const Color careenaGlow = Color(0xFF00F0FF);

  // Shared toolbar/action button colors
  static const Color toolbarButtonBackground = careenaBrand;
  static const Color toolbarButtonForeground = Colors.white;

  static const Color toolbarButtonBackgroundDark = Color(0xFF43B8BE);
  static const Color toolbarButtonForegroundDark = Colors.white;
}
