import 'package:app1/features/symptom_diary/presentation/controllers/symptom_diary_controller.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
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
  });
}
