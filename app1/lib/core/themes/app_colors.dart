import 'package:flutter/material.dart';

/// Shared color tokens for consistent color usage across the application.
class AppColors {
  AppColors._();

  static const Color transparent = Colors.transparent;
  static const Color white = Colors.white;
  static const Color white70 = Color(0xB3FFFFFF);
  static const Color black = Colors.black;
  static const Color black87 = Colors.black87;
  static const Color grey = Colors.grey;
  static const Color greyShade200 = Color(0xFFEEEEEE);
  static const Color greyShade400 = Color(0xFFBDBDBD);
  static const Color greyShade500 = Color(0xFF9E9E9E);
  static const Color red = Colors.red;

  // Brand colors
  static const Color primary = Color(0xFF2F8FA5);
  static const Color accent = Color(0xFF2ECC71);

  // Light mode
  static const Color lightBackground = Colors.white;
  static const Color lightCard = Colors.white;
  static const Color lightTextPrimary = Color(0xFF1F2D3D);
  static const Color lightTextSecondary = Colors.grey;

  // Darkmode
  static const Color darkBackground = Color(0xFF101820);
  static const Color darkCard = Color(0xFF1B2733);
  static const Color darkElevatedSurface = Color(0xFF222A35);
  static const Color darkMutedSurface = Color(0xFF22323D);
  static const Color darkTextPrimary = Color(0xFFF2F5FA);
  static const Color darkTextSecondary = Color(0xFFB0BEC5);

  // Shared page headers
  static const Color headerBackgroundLight = Color(0xFFF4FAFA);
  static const Color headerBackgroundDark = Color(0xFF15212B);

  // Legacy aliases while migrating widgets to Theme.of(context).
  static const Color background = lightBackground;
  static const Color card = lightCard;
  static const Color textPrimary = lightTextPrimary;
  static const Color textSecondary = lightTextSecondary;

  // Existing Careena colors
  static const Color upperBarColor = Color(0xFF1F6F89);
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

  // Home
  static const Color notificationIcon = Color(0xFF8BB5BC);

  // Chat
  static const Color chatBackgroundLight = Color(0xFFF7F9FA);
  static const Color chatAvatarBackgroundDark = Color(0xFF86B2B2);
  static const Color chatAvatarBackgroundLight = Color(0xFFC3E7E7);
  static const Color chatOnlineStatus = Color(0xFF4CAF50);
  static const Color chatInputOuterDark = Color(0xFF1A2029);
  static const Color chatInputInnerDark = Color(0xFF242B36);
  static const Color chatInputAccentDark = Color(0xFF3F8F87);
  static const Color chatInputDisabledDark = Color(0xFF2F3A46);
  static const Color smartReplySurfaceDark = Color(0xFF233338);
  static const Color smartReplyChipDark = Color(0xFF263D40);
  static const Color smartReplyBorderDark = Color(0xFF6FA6A0);
  static const Color smartReplyMutedTextDark = Color(0xFF9DBDBA);
  static const Color symptomListSurfaceLight = Color(0xFFF4F7F6);
  static const Color symptomEditorSurfaceLight = Color(0xFFF7FAF9);
  static const Color symptomEditorText = Color(0xFF36594F);
  static const Color symptomEditorBorder = Color(0xFFB7CCC6);
  static const Color symptomEditorMuted = Color(0xFF6E7E79);

  // Onboarding
  static const Color onboardingBackgroundLight = Color(0xFFE3F4F6);
  static const Color onboardingBubbleDark = Color(0xFFDDE2E3);
  static const Color onboardingBubbleBorderDark = Color(0xFFBCC7C9);

  // Auth and registration
  static const Color authInfoBackgroundDark = Color(0xFF263436);
  static const Color authPrivacyBackgroundDark = Color(0xFF243638);
  static const Color segmentedControlBackgroundDark = Color(0xFF26303C);

  // Warning
  static const Color warningRed = Color(0xFFFF3045);
  static const Color warningBackground = Color(0xFFFFF1F3);
  static const Color warningIconBackground = Color(0xFFFFDCE1);
  static const Color warningEmergencyBackgroundDark = Color(0xFF2F2529);
  static const Color warningReasonBackgroundDark = Color(0xFF3A2A2F);

  // Appointments
  static const Color appointmentInfoBackground = Color(0xFFE8F6F6);
  static const Color appointmentCalendarSurfaceDark = Color(0xFF1B2B3D);
  static const Color appointmentServiceBlue = Color(0xFF2BA4D4);
  static const Color appointmentServicePink = Color(0xFFE91E63);
  static const Color appointmentServiceCardDark = Color(0xFF203246);
  static const Color appointmentServiceCardLight = Color(0xFFF8FAFB);

  // Symptom intensity
  static const Color symptomIntensityNone = Color(0xFF90A4AE);
  static const Color symptomIntensityLow = Color(0xFF3CB878);
  static const Color symptomIntensityMedium = Color(0xFFFFB74D);
  static const Color symptomIntensityHigh = Color(0xFFE57373);

  // Shared toolbar/action button colors
  static const Color toolbarButtonBackground = careenaBrand;
  static const Color toolbarButtonForeground = Colors.white;

  static const Color toolbarButtonBackgroundDark = Color(0xFF43B8BE);
  static const Color toolbarButtonForegroundDark = Colors.white;
}
