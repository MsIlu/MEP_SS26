import 'package:app1/core/themes/app_colors.dart';
import 'package:flutter/material.dart';

InputDecoration medicationInputDecoration({
  required BuildContext context,
  required String label,
  required IconData icon,
  String? hint,
}) {
  final colorScheme = Theme.of(context).colorScheme;

  return InputDecoration(
    labelText: label,
    hintText: hint,
    labelStyle: TextStyle(color: colorScheme.onSurface),
    hintStyle: TextStyle(color: colorScheme.onSurface),
    floatingLabelStyle: TextStyle(
      color: colorScheme.onSurface,
      fontWeight: FontWeight.w600,
    ),
    prefixIcon: Icon(icon, color: colorScheme.onSurface),
    enabledBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(16),
      borderSide: BorderSide(color: AppColors.greyShade400),
    ),
    focusedBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(16),
      borderSide: BorderSide(color: AppColors.greyShade400, width: 2),
    ),
  );
}
