import 'package:app1/features/symptom_diary/data/symptom_import.dart';
import 'package:app1/features/symptom_diary/data/symptom_import_group.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('groups same symptom with same severity and body area', () {
    final groups = groupSymptomImports([
      SymptomImport(
        name: 'Bauchschmerzen',
        severity: 4,
        bodyArea: 'Bauch',
        date: DateTime(2026, 6, 29),
      ),
      SymptomImport(
        name: 'Bauchschmerzen',
        severity: 4,
        bodyArea: 'Bauch',
        date: DateTime(2026, 6, 30),
      ),
      const SymptomImport(name: 'Husten', severity: 2),
    ]);

    expect(groups, hasLength(2));
    expect(groups.first.name, 'Bauchschmerzen');
    expect(groups.first.severity, 4);
    expect(groups.first.bodyArea, 'Bauch');
    expect(groups.first.items.map((item) => item.index), [0, 1]);
    expect(groups.last.name, 'Husten');
    expect(groups.last.items.single.index, 2);
  });

  test('keeps different severities in separate groups', () {
    final groups = groupSymptomImports(const [
      SymptomImport(name: 'Kopfschmerzen', severity: 4),
      SymptomImport(name: 'Kopfschmerzen', severity: 6),
    ]);

    expect(groups, hasLength(2));
    expect(groups.map((group) => group.severity), [4, 6]);
  });

  test('preserves original import indexes for later saving selection', () {
    final groups = groupSymptomImports(const [
      SymptomImport(name: 'Fieber', severity: 8),
      SymptomImport(name: 'Husten', severity: 3),
      SymptomImport(name: 'Fieber', severity: 8),
    ]);

    final feverGroup = groups.firstWhere((group) => group.name == 'Fieber');

    expect(feverGroup.items.map((item) => item.index), [0, 2]);
  });
}