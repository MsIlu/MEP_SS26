const _painKeywords = [
  'schmerz',
  'weh',
  'stech',
  'brenn',
  'druck',
  'zieh',
  'krampf',
];

const _feverKeywords = ['fieber', 'temperatur', 'erhöhte temperatur'];

/// Returns whether a symptom should ask for a body area.
bool symptomNeedsBodyArea(String symptom) {
  final normalizedSymptom = symptom.toLowerCase();
  if (normalizedSymptom.contains('kopfschmerzen') ||
      symptomUsesTemperature(symptom)) {
    return false;
  }

  return _painKeywords.any(normalizedSymptom.contains);
}

/// Returns whether a symptom should capture body temperature instead of pain.
bool symptomUsesTemperature(String symptom) {
  final normalizedSymptom = symptom.toLowerCase();
  return _feverKeywords.any(normalizedSymptom.contains);
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
  if (normalizedSymptom.contains('hals')) {
    return 'Hals';
  }
  if (normalizedSymptom.contains('nacken')) {
    return 'Nacken';
  }
  if (normalizedSymptom.contains('bauch') ||
      normalizedSymptom.contains('magen')) {
    return 'Bauch';
  }
  if (normalizedSymptom.contains('hüfte') ||
      normalizedSymptom.contains('huefte')) {
    return 'Hüfte';
  }
  if (normalizedSymptom.contains('oberschenkel')) {
    return 'Linker Oberschenkel';
  }
  if (normalizedSymptom.contains('geschlecht') ||
      normalizedSymptom.contains('genital') ||
      normalizedSymptom.contains('intim')) {
    return 'Geschlechtsorgan';
  }
  if (normalizedSymptom.contains('rücken')) {
    return 'Rücken';
  }
  if (normalizedSymptom.contains('arm')) {
    return 'Linker Arm';
  }
  if (normalizedSymptom.contains('bein') ||
      normalizedSymptom.contains('knie')) {
    return 'Linkes Knie';
  }
  if (normalizedSymptom.contains('fuß') ||
      normalizedSymptom.contains('fuss') ||
      normalizedSymptom.contains('füße') ||
      normalizedSymptom.contains('fuesse')) {
    return 'Linker Fuß';
  }
  return '';
}
