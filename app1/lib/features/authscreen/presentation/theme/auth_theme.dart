import 'package:flutter/material.dart';
import 'package:app1/core/themes/app_colors.dart';

class AuthTheme {
  static const double fieldRadius = 18;
  static const double buttonRadius = 28;
  static const double screenMaxWidth = 560;
  static const double loginMaxWidth = 520;

  static TextStyle titleStyle(BuildContext context, bool isCompact) {
    final colorScheme = Theme.of(context).colorScheme;

    return TextStyle(
      fontSize: isCompact ? 28 : 32,
      fontWeight: FontWeight.w800,
      color: colorScheme.onSurface,
    );
  }

  static TextStyle bodyStyle(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return TextStyle(
      fontSize: 16,
      height: 1.35,
      color: colorScheme.onSurfaceVariant,
    );
  }

  static TextStyle sectionTitleStyle(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return TextStyle(
      fontSize: 18,
      fontWeight: FontWeight.w800,
      color: colorScheme.onSurface,
    );
  }

  static InputDecoration inputDecoration({
    required BuildContext context,
    required String label,
    required String hint,
    Widget? suffixIcon,
    String? suffixText,
  }) {
    final colorScheme = Theme.of(context).colorScheme;

    return InputDecoration(
      labelText: label,
      hintText: hint,
      filled: true,
      fillColor: colorScheme.surface,
      suffixIcon: suffixIcon,
      suffixText: suffixText,
      labelStyle: TextStyle(color: colorScheme.onSurface),
      hintStyle: TextStyle(color: colorScheme.onSurface),
      prefixIconColor: colorScheme.onSurface,
      suffixIconColor: colorScheme.onSurface,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(fieldRadius),
        borderSide: BorderSide(color: AppColors.greyShade400),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(fieldRadius),
        borderSide: BorderSide(color: AppColors.greyShade400),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(fieldRadius),
        borderSide: BorderSide(color: AppColors.greyShade400, width: 2),
      ),
    );
  }
}
