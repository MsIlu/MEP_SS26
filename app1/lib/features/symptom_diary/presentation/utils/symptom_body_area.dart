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
  return _painKeywords.any(normalizedSymptom.contains);
}

/// Suggests a likely body area from common symptom wording.
String suggestedBodyAreaForSymptom(String symptom) {
  final normalizedSymptom = symptom.toLowerCase();
  if (normalizedSymptom.contains('kopf')) {
    return 'Kopf';
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
  if (normalizedSymptom.contains('arm')) {
    return 'Linker Arm';
  }
  if (normalizedSymptom.contains('bein') ||
      normalizedSymptom.contains('knie')) {
    return 'Linkes Bein';
  }
  return '';
}