import 'package:app1/features/symptom_diary/presentation/utils/symptom_body_area.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('symptomNeedsBodyArea', () {
    test('returns false for Kopfschmerzen so the body area step is skipped', () {
      expect(symptomNeedsBodyArea('Kopfschmerzen'), isFalse);
    });

    test('returns true for generic Schmerzen that require a body area', () {
      expect(symptomNeedsBodyArea('Arm schmerzen'), isTrue);
    });
  });

  group('suggestedBodyAreaForSymptom', () {

    test('returns Kopf for other symptoms mentioning Kopf', () {
      expect(suggestedBodyAreaForSymptom('Kopfweh'), 'Kopf');
    });
  });
}
