const _painKeywords = [
  'schmerz',
  'weh',
  'stech',
  'brenn',
  'druck',
  'zieh',
  'krampf',
];

/// Returns whether a symptom should ask for a body area.
bool symptomNeedsBodyArea(String symptom) {
  final normalizedSymptom = symptom.toLowerCase();
  if (normalizedSymptom.contains('kopfschmerzen')) {
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
    return 'Vorne: Kopf';
  }
  if (normalizedSymptom.contains('hals') ||
      normalizedSymptom.contains('nacken')) {
    return 'Vorne: Hals';
  }
  if (normalizedSymptom.contains('brust')) {
    return 'Vorne: Brust';
  }
  if (normalizedSymptom.contains('bauch') ||
      normalizedSymptom.contains('magen')) {
    return 'Vorne: Bauch';
  }
  if (normalizedSymptom.contains('rücken')) {
    return 'Hinten: Rücken';
  }
  if (normalizedSymptom.contains('hüfte') ||
      normalizedSymptom.contains('huefte')) {
    return 'Vorne: Hüfte';
  }
  if (normalizedSymptom.contains('knie')) {
    return 'Vorne: Knie';
  }
  if (normalizedSymptom.contains('fuß') ||
      normalizedSymptom.contains('fuss') ||
      normalizedSymptom.contains('füße') ||
      normalizedSymptom.contains('fuesse')) {
    return 'Vorne: Füße';
  }
  if (normalizedSymptom.contains('arm')) {
    return 'Vorne: Linker Arm';
  }
  if (normalizedSymptom.contains('bein')) {
    return 'Vorne: Linkes Bein';
  }
  return '';
}
