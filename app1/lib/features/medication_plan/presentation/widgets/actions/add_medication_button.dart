import 'package:app1/features/chatscreen/presentation/themes/app_colors.dart';
import 'package:flutter/material.dart';

/// Floating-style action button that opens the medication creation dialog.
class AddMedicationButton extends StatelessWidget {
  final VoidCallback onPressed;

  const AddMedicationButton({super.key, required this.onPressed});

  @override
  Widget build(BuildContext context) {
    return IconButton.filled(
      tooltip: 'Medikament hinzufügen',
      style: IconButton.styleFrom(
        backgroundColor: AppColors.toolbarButtonBackground,
        foregroundColor: AppColors.toolbarButtonForeground,
        fixedSize: const Size(48, 48),
      ),
      onPressed: onPressed,
      icon: const Icon(Icons.add),
    );
  }
}