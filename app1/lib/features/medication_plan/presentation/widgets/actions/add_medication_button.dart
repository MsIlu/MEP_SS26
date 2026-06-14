import 'package:app1/core/widgets/careena_action_buttons.dart';
import 'package:flutter/material.dart';

/// Floating-style action button that opens the medication creation dialog.
class AddMedicationButton extends StatelessWidget {
  final VoidCallback onPressed;

  const AddMedicationButton({super.key, required this.onPressed});

  @override
  Widget build(BuildContext context) {
    return CareenaIconActionButton.add(
      tooltip: 'Medikament hinzufügen',
      onPressed: onPressed,
    );
  }
}