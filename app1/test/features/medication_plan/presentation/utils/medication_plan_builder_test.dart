import 'package:app1/features/medication_plan/data/medication_entry.dart';
import 'package:app1/features/medication_plan/data/medication_schedule.dart';
import 'package:app1/features/medication_plan/presentation/utils/medication_plan_builder.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('plannedMedicationDosesForDate', () {
    test('returns no doses before the medication was added', () {
      // The selected day must respect the medication creation date.
      final doses = plannedMedicationDosesForDate([
        _entry(createdAt: DateTime(2026, 6, 2)),
      ], DateTime(2026, 6, 1));

      expect(doses, isEmpty);
    });

    test('expands twice daily medication into two ordered dose rows', () {
      // Dose rows are sorted by time even if the entry stores them differently.
      final doses = plannedMedicationDosesForDate([
        _entry(
          frequency: MedicationFrequency.twiceDaily,
          intakeTime: const TimeOfDay(hour: 20, minute: 0),
          secondIntakeTime: const TimeOfDay(hour: 8, minute: 30),
        ),
      ], DateTime(2026, 6, 2));

      expect(doses, hasLength(2));
      expect(doses[0].doseIndex, 0);
      expect(doses[0].intakeTime, const TimeOfDay(hour: 8, minute: 30));
      expect(doses[1].doseIndex, 1);
      expect(doses[1].intakeTime, const TimeOfDay(hour: 20, minute: 0));
    });

    test('filters weekly and monthly schedules by their start day', () {
      // June 2, 2026 is the anchor day for both weekly and monthly schedules.
      final entries = [
        _entry(
          id: 1,
          name: 'Wöchentliches Medikament',
          frequency: MedicationFrequency.weekly,
          createdAt: DateTime(2026, 6, 2),
        ),
        _entry(
          id: 2,
          name: 'Monatliches Medikament',
          frequency: MedicationFrequency.monthly,
          createdAt: DateTime(2026, 6, 2),
        ),
      ];

      final anchorDay = plannedMedicationDosesForDate(
        entries,
        DateTime(2026, 6, 2),
      );
      final nextDay = plannedMedicationDosesForDate(
        entries,
        DateTime(2026, 6, 3),
      );
      final nextMonthAnchor = plannedMedicationDosesForDate(
        entries,
        DateTime(2026, 7, 2),
      );

      expect(anchorDay.map((dose) => dose.entry.name), [
        'Wöchentliches Medikament',
        'Monatliches Medikament',
      ]);
      expect(nextDay, isEmpty);
      expect(nextMonthAnchor.map((dose) => dose.entry.name), [
        'Monatliches Medikament',
      ]);
    });

    test('marks weekdays but not weekends as planned', () {
      // Weekday schedules should appear from Monday through Friday only.
      final entries = [
        _entry(
          frequency: MedicationFrequency.weekdays,
          createdAt: DateTime(2026, 6, 1),
        ),
      ];

      expect(hasMedicationPlanForDate(entries, DateTime(2026, 6, 5)), isTrue);
      expect(hasMedicationPlanForDate(entries, DateTime(2026, 6, 6)), isFalse);
    });
  });
}

MedicationEntry _entry({
  int id = 1,
  String name = 'Ibuprofen',
  MedicationFrequency frequency = MedicationFrequency.daily,
  TimeOfDay intakeTime = const TimeOfDay(hour: 8, minute: 0),
  TimeOfDay? secondIntakeTime,
  DateTime? createdAt,
}) {
  return MedicationEntry(
    id: id,
    name: name,
    dose: '400 mg',
    intakeTime: intakeTime,
    secondIntakeTime: secondIntakeTime,
    frequency: frequency,
    remindersEnabled: true,
    createdAt: createdAt ?? DateTime(2026, 6, 2),
  );
}
