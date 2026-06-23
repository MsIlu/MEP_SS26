const _painKeywords = [
  'schmerz',
  'weh',
  'stech',
  'brenn',
  'druck',
  'zieh',
  'krampf',
];

const _specificPainSymptoms = [
  'kopfschmerz',
  'kopfschmerzen',
];

/// Returns whether a symptom should ask for a body area.
bool symptomNeedsBodyArea(String symptom) {
  final normalizedSymptom = symptom.toLowerCase();
  if (_specificPainSymptoms.any(normalizedSymptom.contains)) {
    return false;
  }

  return _painKeywords.any(normalizedSymptom.contains);
}

/// Returns whether the symptom should ask for body temperature instead.
bool symptomUsesTemperature(String symptom) {
  final normalizedSymptom = symptom.toLowerCase();
  return normalizedSymptom.contains('fieber') ||
      normalizedSymptom.contains('temperatur');
}

/// Suggests a likely body area from common symptom wording.
String suggestedBodyAreaForSymptom(String symptom) {
  final normalizedSymptom = symptom.toLowerCase();
  if (normalizedSymptom.contains('kopf')) {
    return 'Kopf';
  }
  if (normalizedSymptom.contains('hals') ||
      normalizedSymptom.contains('nacken')) {
    return 'Hals';
  }
  if (normalizedSymptom.contains('brust')) {
    return 'Brust';
  }
  if (normalizedSymptom.contains('bauch') ||
      normalizedSymptom.contains('magen')) {
    return 'Bauch';
  }
  if (normalizedSymptom.contains('rücken')) {
    return 'Rücken';
  }
  if (normalizedSymptom.contains('hüfte') ||
      normalizedSymptom.contains('huefte')) {
    return 'Hüfte';
  }
  if (normalizedSymptom.contains('knie')) {
    return 'Knie';
  }
  if (normalizedSymptom.contains('fuß') ||
      normalizedSymptom.contains('fuss') ||
      normalizedSymptom.contains('füße') ||
      normalizedSymptom.contains('fuesse')) {
    return 'Füße';
  }
  if (normalizedSymptom.contains('arm')) {
    return 'Linker Arm';
  }
  if (normalizedSymptom.contains('bein')) {
    return 'Linkes Bein';
  }
  return '';
}
