import 'package:app1/features/medication_plan/data/medication_entry.dart';
import 'package:app1/features/medication_plan/data/medication_repository.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  // Test case references: documents/Testfaelle_Frontend.md#t01-medicationbook
  group('MedicationRepository', () {
    setUp(() {
      SharedPreferences.setMockInitialValues({});
    });

    test('T01.3.1 loads an empty list when no medication is stored', () async {
      final repository = MedicationRepository();

      expect(await repository.loadEntries(), isEmpty);
    });

    test(
      'T01.3.2 saves and reloads medication entries from local storage',
      () async {
        final repository = MedicationRepository();
        final entry = _entry(name: 'Ibuprofen');

        await repository.saveEntries([entry]);

        final entries = await repository.loadEntries();
        expect(entries, hasLength(1));
        expect(entries.single.name, 'Ibuprofen');
        expect(entries.single.dose, '400 mg');
      },
    );

    test(
      'T01.3.3 returns stored entries sorted by first intake time',
      () async {
        final repository = MedicationRepository();

        await repository.saveEntries([
          _entry(
            name: 'Abends',
            intakeTime: const TimeOfDay(hour: 21, minute: 0),
          ),
          _entry(
            name: 'Morgens',
            intakeTime: const TimeOfDay(hour: 7, minute: 30),
          ),
        ]);

        final entries = await repository.loadEntries();

        expect(entries.map((entry) => entry.name), ['Morgens', 'Abends']);
      },
    );
  });
}

MedicationEntry _entry({
  String name = 'Ibuprofen',
  TimeOfDay intakeTime = const TimeOfDay(hour: 8, minute: 0),
}) {
  return MedicationEntry(
    id: name.hashCode,
    name: name,
    dose: '400 mg',
    intakeTime: intakeTime,
    remindersEnabled: true,
    createdAt: DateTime(2026, 6, 2),
  );
}
