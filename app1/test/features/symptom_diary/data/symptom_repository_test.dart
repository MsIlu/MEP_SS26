import 'package:app1/features/symptom_diary/data/symptom_entry.dart';
import 'package:app1/features/symptom_diary/data/symptom_repository.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  group('SymptomRepository', () {
    setUp(() => SharedPreferences.setMockInitialValues({}));

    test('keeps offline entries separated by profile id', () async {
      final repository = SymptomRepository();
      final annaEntry = _entry(1, 'Kopfschmerzen');
      final philippEntry = _entry(2, 'Husten');

      await repository.saveEntries(profileId: 11, entries: [annaEntry]);
      await repository.saveEntries(profileId: 12, entries: [philippEntry]);

      expect(
        (await repository.loadEntries(profileId: 11)).single.symptom,
        'Kopfschmerzen',
      );
      expect(
        (await repository.loadEntries(profileId: 12)).single.symptom,
        'Husten',
      );
    });

    test('clears only the selected profile cache', () async {
      final repository = SymptomRepository();
      await repository.saveEntries(
        profileId: 11,
        entries: [_entry(1, 'Kopfschmerzen')],
      );
      await repository.saveEntries(
        profileId: 12,
        entries: [_entry(2, 'Husten')],
      );

      await repository.clearEntries(profileId: 11);

      expect(await repository.loadEntries(profileId: 11), isEmpty);
      expect(await repository.loadEntries(profileId: 12), hasLength(1));
    });

    test('keeps pending deletions separated by profile id', () async {
      final repository = SymptomRepository();

      await repository.addPendingDelete(profileId: 11, entryId: 101);
      await repository.addPendingDelete(profileId: 12, entryId: 202);
      await repository.removePendingDelete(profileId: 11, entryId: 101);

      expect(await repository.loadPendingDeleteIds(profileId: 11), isEmpty);
      expect(await repository.loadPendingDeleteIds(profileId: 12), {202});
    });
  });
}

SymptomEntry _entry(int id, String symptom) {
  return SymptomEntry(
    id: id,
    date: DateTime(2026, 6, 30),
    symptom: symptom,
    intensity: 5,
    note: '',
    createdAt: DateTime(2026, 6, 30, 10),
  );
}
