import 'package:app1/features/medication_plan/data/medication_entry.dart';
import 'package:app1/features/medication_plan/data/medication_schedule.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  // Test case references: documents/Testfaelle_Frontend_Aufgaben.md#t01-medicationbook
  group('MedicationEntry', () {
    test('T01.2.1 preserves schedule, second dose, and taken state in JSON', () {
      final entry = MedicationEntry(
        id: 7,
        name: 'Ibuprofen',
        dose: '400 mg',
        intakeTime: const TimeOfDay(hour: 8, minute: 0),
        secondIntakeTime: const TimeOfDay(hour: 20, minute: 30),
        frequency: MedicationFrequency.twiceDaily,
        remindersEnabled: false,
        createdAt: DateTime(2026, 6, 2),
        takenDateKeys: const ['2026-06-02#0'],
      );

      final decoded = MedicationEntry.decode(entry.encode());

      expect(decoded.id, 7);
      expect(decoded.name, 'Ibuprofen');
      expect(decoded.dose, '400 mg');
      expect(decoded.intakeTime, const TimeOfDay(hour: 8, minute: 0));
      expect(decoded.secondIntakeTime, const TimeOfDay(hour: 20, minute: 30));
      expect(decoded.frequency, MedicationFrequency.twiceDaily);
      expect(decoded.remindersEnabled, isFalse);
      expect(decoded.createdAt, DateTime(2026, 6, 2));
      expect(decoded.takenDateKeys, ['2026-06-02#0']);
    });

    test('T01.2.2 restores legacy entries with safe defaults', () {
      final entry = MedicationEntry.fromJson({
        'id': 3,
        'name': 'Paracetamol',
        'dose': '500 mg',
        'hour': 9,
        'minute': 45,
      });

      expect(entry.frequency, MedicationFrequency.daily);
      expect(entry.remindersEnabled, isTrue);
      expect(entry.takenDateKeys, isEmpty);
      expect(entry.intakeTimes, [const TimeOfDay(hour: 9, minute: 45)]);
    });

    test('T01.2.3 plans weekly medication only on the anchor weekday', () {
      final entry = _entry(
        frequency: MedicationFrequency.weekly,
        createdAt: DateTime(2026, 6, 2),
      );

      expect(entry.isPlannedOn(DateTime(2026, 6, 2)), isTrue);
      expect(entry.isPlannedOn(DateTime(2026, 6, 9)), isTrue);
      expect(entry.isPlannedOn(DateTime(2026, 6, 10)), isFalse);
    });
  });
}

MedicationEntry _entry({
  MedicationFrequency frequency = MedicationFrequency.daily,
  DateTime? createdAt,
}) {
  return MedicationEntry(
    id: 1,
    name: 'Ibuprofen',
    dose: '400 mg',
    intakeTime: const TimeOfDay(hour: 8, minute: 0),
    frequency: frequency,
    remindersEnabled: true,
    createdAt: createdAt ?? DateTime(2026, 6, 2),
  );
}
