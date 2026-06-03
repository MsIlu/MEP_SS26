import 'package:app1/features/chatscreen/presentation/themes/app_colors.dart';
import 'package:flutter/material.dart';

import '../../../data/medication_entry.dart';
import '../../../data/medication_schedule.dart';
import '../../models/planned_medication_dose.dart';
import '../../utils/medication_date_format.dart';
import '../../utils/medication_time_format.dart';
import 'taken_checkbox.dart';

/// Renders one scheduled dose in the selected day's medication plan.
class PlannedMedicationRow extends StatelessWidget {
  final PlannedMedicationDose dose;
  final DateTime selectedDate;
  final DateTime today;
  final void Function(
    MedicationEntry entry,
    DateTime date,
    int doseIndex,
    bool isTaken,
  )
  onTakenChanged;

  const PlannedMedicationRow({
    super.key,
    required this.dose,
    required this.selectedDate,
    required this.today,
    required this.onTakenChanged,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    final entry = dose.entry;
    final isTaken = entry.takenDateKeys.contains(
      medicationDoseDateKey(selectedDate, dose.doseIndex),
    );
    final canMarkTaken = !_isFutureMedicationDay(selectedDate, today);

    final takenSurfaceColor = isDarkMode
        ? colorScheme.surfaceContainerHighest.withValues(alpha: 0.72)
        : AppColors.careenaBubbleBackground.withValues(alpha: 0.55);
    final takenBorderColor = AppColors.careenaTeal.withValues(alpha: 0.42);

    return AnimatedContainer(
      duration: const Duration(milliseconds: 180),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: isTaken ? takenSurfaceColor : colorScheme.surface,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(
          color: isTaken
              ? takenBorderColor
              : isDarkMode
              ? colorScheme.outlineVariant.withValues(alpha: 0.55)
              : AppColors.careenaBorder,
        ),
      ),
      child: Row(
        children: [
          Container(
            width: 48,
            height: 48,
            alignment: Alignment.center,
            decoration: BoxDecoration(
              color: AppColors.careenaBrand.withValues(
                alpha: isTaken ? 0.2 : 0.14,
              ),
              borderRadius: BorderRadius.circular(14),
            ),
            child: Icon(
              isTaken ? Icons.check_rounded : Icons.schedule,
              color: AppColors.careenaTeal,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  formatMedicationTime(dose.intakeTime),
                  style: const TextStyle(
                    color: AppColors.careenaTeal,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                const SizedBox(height: 3),
                Text(
                  entry.name,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(
                    color: colorScheme.onSurface,
                    fontWeight: FontWeight.w800,
                    decoration: isTaken ? TextDecoration.lineThrough : null,
                    decorationColor: AppColors.careenaTeal,
                    decorationThickness: 1.4,
                  ),
                ),
                Text(
                  entry.frequency == MedicationFrequency.twiceDaily
                      ? '${entry.dose} - Einnahme ${dose.doseIndex + 1}'
                      : entry.dose,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(color: colorScheme.onSurfaceVariant),
                ),
              ],
            ),
          ),
          TakenCheckbox(
            value: isTaken,
            enabled: canMarkTaken,
            onChanged: (value) {
              onTakenChanged(entry, selectedDate, dose.doseIndex, value);
            },
          ),
        ],
      ),
    );
  }
}

/// Returns whether the selected day is after today, ignoring clock time.
bool _isFutureMedicationDay(DateTime date, DateTime today) {
  final selectedDay = DateTime(date.year, date.month, date.day);
  final currentDay = DateTime(today.year, today.month, today.day);

  return selectedDay.isAfter(currentDay);
}
