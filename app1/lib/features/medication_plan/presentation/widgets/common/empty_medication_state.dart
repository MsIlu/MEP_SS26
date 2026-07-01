import 'package:app1/core/widgets/careena_empty_state.dart';
import 'package:flutter/material.dart';

/// Empty state shown before the user saves the first medication.
class EmptyMedicationState extends StatelessWidget {
  const EmptyMedicationState({super.key});

  @override
  Widget build(BuildContext context) {
    return const CareenaEmptyState(
      icon: Icons.medication_outlined,
      title: 'Noch keine Medikamente vorhanden',
      message:
          'Trage dein erstes Medikament ein und aktiviere die tägliche Erinnerung.',
    );
  }
}
