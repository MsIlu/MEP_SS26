import 'package:app1/core/widgets/careena_action_buttons.dart';
import 'package:flutter/material.dart';

/// Floating-style action button for opening the symptom entry dialog.
class SymptomAddButton extends StatelessWidget {
  final VoidCallback onPressed;

  const SymptomAddButton({super.key, required this.onPressed});

  @override
  Widget build(BuildContext context) {
    return CareenaIconActionButton.add(
      tooltip: 'Symptom eintragen',
      onPressed: onPressed,
    );
  }
}
