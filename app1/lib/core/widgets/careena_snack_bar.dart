import 'package:flutter/material.dart';
import '../themes/app_colors.dart';

/// Shows short app feedback with the same bottom bar style everywhere.
void showCareenaSnackBar(BuildContext context, String message) {
  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(
      backgroundColor: AppColors.careenaTeal,
      content: Text(
        message,
        style: const TextStyle(
          color: AppColors.white,
          fontWeight: FontWeight.bold,
          fontSize: 16,
        ),
      ),
    ),
  );
}
