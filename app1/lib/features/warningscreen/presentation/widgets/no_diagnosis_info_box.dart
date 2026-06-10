import 'package:flutter/material.dart';

import 'package:app1/core/themes/app_colors.dart';
import '../theme/warning_copy.dart';
import '../theme/warning_theme.dart';

/// Reminder that the warning screen is not a medical diagnosis.
class NoDiagnosisInfoBox extends StatelessWidget {
  const NoDiagnosisInfoBox({super.key});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    final iconColor = isDarkMode
        ? AppColors.toolbarButtonBackgroundDark
        : WarningColors.teal;

    final textColor = isDarkMode
        ? colorScheme.onSurfaceVariant
        : WarningColors.darkText;

    return Container(
      padding: const EdgeInsets.all(14),
      decoration: WarningDecorations.infoBox(context),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.info_outline, color: iconColor, size: 20),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              WarningCopy.noDiagnosis,
              style: TextStyle(color: textColor, fontSize: 12, height: 1.35),
            ),
          ),
        ],
      ),
    );
  }
}