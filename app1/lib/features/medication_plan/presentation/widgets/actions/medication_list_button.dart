import 'package:app1/core/themes/app_colors.dart';
import 'package:flutter/material.dart';

/// Opens the saved medication management dialog from the bottom action bar.
class MedicationListButton extends StatelessWidget {
  final VoidCallback onPressed;

  const MedicationListButton({super.key, required this.onPressed});

  @override
  Widget build(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return FilledButton.icon(
      onPressed: onPressed,
      icon: const Icon(Icons.medication_outlined, size: 22),
      label: const Text('Meine Medikamente'),
      style: FilledButton.styleFrom(
        backgroundColor: isDarkMode
            ? AppColors.darkMutedSurface
            : AppColors.careenaBrand,
        foregroundColor: AppColors.white,
        minimumSize: const Size(0, 54),
        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
        textStyle: Theme.of(context)
            .textTheme
            .labelLarge
            ?.copyWith(fontWeight: FontWeight.w700),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
      ),
    );
  }
}