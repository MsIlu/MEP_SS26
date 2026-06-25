import 'package:flutter/material.dart';

import 'package:app1/core/themes/app_colors.dart';

/// Short reassurance shown next to the explicit consent checkbox.
class PrivacyNote extends StatelessWidget {
  const PrivacyNote({super.key});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    final backgroundColor = isDarkMode
        ? AppColors.authPrivacyBackgroundDark
        : AppColors.careenaNoteBackground;

    final borderColor = isDarkMode
        ? AppColors.toolbarButtonBackgroundDark.withValues(alpha: 0.55)
        : AppColors.careenaSoftAccent;

    final contentColor = isDarkMode
        ? colorScheme.onSurface
        : AppColors.careenaTitle;

    return DecoratedBox(
      decoration: BoxDecoration(
        color: backgroundColor,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: borderColor),
      ),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Row(
          children: [
            Icon(Icons.lock_outline, color: contentColor),
            const SizedBox(width: 10),
            Expanded(
              child: Text(
                'Deine Daten sind bei uns sicher und werden vertraulich behandelt.',
                style: TextStyle(
                  color: contentColor,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
