import 'package:app1/features/chatscreen/presentation/themes/app_colors.dart';
import 'package:flutter/material.dart';

/// Empty state shown before the user saves the first medication.
class EmptyMedicationState extends StatelessWidget {
  const EmptyMedicationState({super.key});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Container(
      padding: const EdgeInsets.all(22),
      decoration: BoxDecoration(
        color: colorScheme.surface,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppColors.careenaBorder),
      ),
      child: Column(
        children: [
          Icon(
            Icons.medication_outlined,
            color: colorScheme.onSurfaceVariant,
            size: 34,
          ),
          const SizedBox(height: 10),
          Text(
            'Noch keine Medikamente gespeichert',
            textAlign: TextAlign.center,
            style: TextStyle(
              color: colorScheme.onSurface,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            'Trage dein erstes Medikament ein und aktiviere die tägliche Erinnerung.',
            textAlign: TextAlign.center,
            style: TextStyle(color: colorScheme.onSurfaceVariant),
          ),
        ],
      ),
    );
  }
}