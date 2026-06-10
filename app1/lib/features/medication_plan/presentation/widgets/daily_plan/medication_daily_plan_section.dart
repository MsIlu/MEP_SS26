import 'package:flutter/material.dart';

import '../../../data/medication_entry.dart';
import '../../utils/medication_date_format.dart';
import '../../utils/medication_plan_builder.dart';
import 'empty_plan_pill.dart';
import 'planned_medication_row.dart';

/// Shows medications planned for the selected day.
class MedicationDailyPlanSection extends StatelessWidget {
  final DateTime selectedDate;
  final DateTime today;
  final List<MedicationEntry> entries;
  final void Function(
    MedicationEntry entry,
    DateTime date,
    int doseIndex,
    bool isTaken,
  )
  onTakenChanged;

  const MedicationDailyPlanSection({
    super.key,
    required this.selectedDate,
    required this.today,
    required this.entries,
    required this.onTakenChanged,
  });

  @override
  Widget build(BuildContext context) {
    final plannedDoses = plannedMedicationDosesForDate(entries, selectedDate);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          isSameMedicationDay(selectedDate, today)
              ? 'Heute geplant'
              : 'Für diesen Tag geplant',
          style: TextStyle(
            color: Theme.of(context).colorScheme.onSurface,
            fontSize: 18,
            fontWeight: FontWeight.w800,
          ),
        ),
        const SizedBox(height: 10),
        if (plannedDoses.isEmpty)
          const EmptyPlanPill()
        else
          ...plannedDoses.map(
            (dose) => Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: PlannedMedicationRow(
                dose: dose,
                selectedDate: selectedDate,
                today: today,
                onTakenChanged: onTakenChanged,
              ),
            ),
          ),
      ],
    );
  }
}
