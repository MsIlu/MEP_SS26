import '../../data/medication_entry.dart';
import '../models/planned_medication_dose.dart';

/// Expands medication entries into the dose rows planned for a calendar day.
List<PlannedMedicationDose> plannedMedicationDosesForDate(
  List<MedicationEntry> entries,
  DateTime date,
) {
  final plannedDoses = <PlannedMedicationDose>[];

  for (final entry in entries) {
    if (!entry.isPlannedOn(date)) {
      continue;
    }

    final times = entry.intakeTimes;
    for (var index = 0; index < times.length; index++) {
      plannedDoses.add(
        PlannedMedicationDose(
          entry: entry,
          doseIndex: index,
          intakeTime: times[index],
        ),
      );
    }
  }

  plannedDoses.sort((first, second) {
    final firstMinutes = first.intakeTime.hour * 60 + first.intakeTime.minute;
    final secondMinutes =
        second.intakeTime.hour * 60 + second.intakeTime.minute;

    return firstMinutes.compareTo(secondMinutes);
  });

  return plannedDoses;
}

/// Returns whether the calendar day has at least one planned medication dose.
bool hasMedicationPlanForDate(List<MedicationEntry> entries, DateTime date) {
  return entries.any((entry) => entry.isPlannedOn(date));
}