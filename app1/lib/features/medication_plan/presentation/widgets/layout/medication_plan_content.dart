import 'package:flutter/material.dart';

import '../../../data/medication_entry.dart';
import '../actions/medication_bottom_actions.dart';
import '../daily_plan/medication_daily_plan_section.dart';
import '../day_selector/medication_day_selector.dart';

/// Main medication plan layout framed by top navigation and bottom actions.
class MedicationPlanContent extends StatelessWidget {
  final DateTime selectedDate;
  final DateTime today;
  final List<MedicationEntry> entries;
  final ValueChanged<DateTime> onDateSelected;
  final VoidCallback onOpenMedicationList;
  final VoidCallback onAddMedication;
  final void Function(
    MedicationEntry entry,
    DateTime date,
    int doseIndex,
    bool isTaken,
  )
  onTakenChanged;

  const MedicationPlanContent({
    super.key,
    required this.selectedDate,
    required this.today,
    required this.entries,
    required this.onDateSelected,
    required this.onOpenMedicationList,
    required this.onAddMedication,
    required this.onTakenChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Expanded(
          child: SingleChildScrollView(
            padding: const EdgeInsets.only(bottom: 20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                MedicationDaySelector(
                  selectedDate: selectedDate,
                  today: today,
                  entries: entries,
                  onDateSelected: onDateSelected,
                ),
                const SizedBox(height: 22),
                MedicationDailyPlanSection(
                  selectedDate: selectedDate,
                  today: today,
                  entries: entries,
                  onTakenChanged: onTakenChanged,
                ),
              ],
            ),
          ),
        ),
        MedicationBottomActions(
          onOpenMedicationList: onOpenMedicationList,
          onAddMedication: onAddMedication,
        ),
      ],
    );
  }
}
