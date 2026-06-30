import 'package:app1/features/symptom_diary/presentation/controllers/symptom_diary_controller.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  // Test case references: documents/Testfaelle_Frontend.md#t09-symptom-diary
  group('SymptomDiaryController', () {
    setUp(() {
      SharedPreferences.setMockInitialValues({});
    });

    test(
      'stores entries for the selected day and calculates the average',
      () async {
        // The controller is the source for both daily lists and summary cards.
        final controller = SymptomDiaryController();
        addTearDown(controller.dispose);

        await controller.loadEntries();
        await controller.addEntry(
          date: DateTime(2026, 6, 2),
          symptom: 'Kopfschmerzen',
          bodyArea: 'Kopf',
          intensity: 4,
          note: 'Nach dem Aufstehen',
        );
        await controller.addEntry(
          date: DateTime(2026, 6, 2),
          symptom: 'Übelkeit',
          intensity: 8,
          note: '',
        );

        final entries = controller.entriesForDate(DateTime(2026, 6, 2));

        expect(entries, hasLength(2));
        expect(entries.first.symptom, 'Kopfschmerzen');
        expect(entries.first.bodyArea, 'Kopf');
        expect(controller.averageIntensityForDate(DateTime(2026, 6, 2)), 6);
        expect(controller.entriesForDate(DateTime(2026, 6, 3)), isEmpty);
      },
    );

    test('updates an existing entry', () async {
      final controller = SymptomDiaryController();
      addTearDown(controller.dispose);

      await controller.loadEntries();
      final entry = await controller.addEntry(
        date: DateTime(2026, 6, 2),
        symptom: 'Kopfschmerzen',
        bodyArea: 'Kopf',
        intensity: 4,
        note: 'Morgens',
      );

      await controller.updateEntry(
        entry: entry,
        symptom: 'Bauchschmerzen',
        bodyArea: 'Bauch',
        intensity: 7,
        note: 'Nach dem Essen',
      );

      final updated = controller.entriesForDate(DateTime(2026, 6, 2)).single;

      expect(updated.id, entry.id);
      expect(updated.symptom, 'Bauchschmerzen');
      expect(updated.bodyArea, 'Bauch');
      expect(updated.intensity, 7);
      expect(updated.note, 'Nach dem Essen');
      expect(updated.createdAt, entry.createdAt);
    });
  });
}
