import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../../../chatscreen/presentation/themes/app_colors.dart';

class AuthTheme {
  static const double fieldRadius = 18;
  static const double buttonRadius = 28;
  static const double screenMaxWidth = 560;
  static const double loginMaxWidth = 520;

  static TextStyle titleStyle(bool isCompact) {
    return GoogleFonts.nunito(
      fontSize: isCompact ? 28 : 32,
      fontWeight: FontWeight.w800,
      color: AppColors.careenaTitle,
    );
  }

  static TextStyle bodyStyle() {
    return GoogleFonts.nunito(
      fontSize: 16,
      height: 1.35,
      color: AppColors.careenaBody,
    );
  }

  static TextStyle sectionTitleStyle() {
    return GoogleFonts.nunito(
      fontSize: 18,
      fontWeight: FontWeight.w800,
      color: AppColors.careenaTitle,
    );
  }

  static InputDecoration inputDecoration({
    required String label,
    required String hint,
    Widget? suffixIcon,
    String? suffixText,
  }) {
    return InputDecoration(
      labelText: label,
      hintText: hint,
      filled: true,
      fillColor: Colors.white,
      suffixIcon: suffixIcon,
      suffixText: suffixText,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(fieldRadius),
        borderSide: BorderSide.none,
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(fieldRadius),
        borderSide: const BorderSide(color: AppColors.careenaBorder),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(fieldRadius),
        borderSide: const BorderSide(color: AppColors.careenaPrimary, width: 2),
      ),
    );
  }
}