import 'package:app1/core/themes/app_colors.dart';
import 'package:flutter/material.dart';

/// Shared short feature explanation shown at the top of feature screens.
class CareenaInfoCard extends StatelessWidget {
  final String text;
  final IconData icon;

  const CareenaInfoCard({
    super.key,
    required this.text,
    this.icon = Icons.tips_and_updates_outlined,
  });

  @override
  Widget build(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    final colorScheme = Theme.of(context).colorScheme;

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: isDarkMode ? colorScheme.surface : AppColors.appointmentInfoBackground,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.careenaTeal, width: 1.5),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(
            icon,
            color: isDarkMode ? AppColors.white : AppColors.careenaTeal,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(text, style: TextStyle(color: colorScheme.onSurface)),
          ),
        ],
      ),
    );
  }
}
