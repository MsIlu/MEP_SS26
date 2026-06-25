import 'package:app1/core/themes/app_colors.dart';
import 'package:flutter/material.dart';

/// Compact empty state for days without planned medication doses.
class EmptyPlanPill extends StatelessWidget {
  const EmptyPlanPill({super.key});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      decoration: BoxDecoration(
        color: Theme.of(context).brightness == Brightness.dark
            ? AppColors.darkElevatedSurface
            : AppColors.lightBackground,
        borderRadius: BorderRadius.circular(18),
      ),
      child: Text(
        'Keine Medikamente geplant',
        style: TextStyle(
          color: colorScheme.onSurfaceVariant,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}
