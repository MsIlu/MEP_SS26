import 'package:app1/core/widgets/shared_day_selector.dart';
import 'package:flutter/material.dart';
import '../../../data/medication_entry.dart';
import '../../utils/medication_plan_builder.dart';

/// Medication-specific adapter for the shared horizontal day selector.
class MedicationDaySelector extends StatelessWidget {
  final DateTime selectedDate;
  final DateTime today;
  final List<MedicationEntry> entries;
  final ValueChanged<DateTime> onDateSelected;

  const MedicationDaySelector({
    super.key,
    required this.selectedDate,
    required this.today,
    required this.entries,
    required this.onDateSelected,
  });

  @override
  Widget build(BuildContext context) {
    return SharedDaySelector(
      selectedDate: selectedDate,
      today: today,
      hasMarker: (date) => hasMedicationPlanForDate(entries, date),
      onDateSelected: onDateSelected,
    );
  }
}
