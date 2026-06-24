/// Small glossary entry used to explain medical language inside chat replies.
class MedicalTerm {
  /// Word or phrase that should be detected in a response.
  final String term;

  /// Plain-language explanation shown to the user.
  final String explanation;

  const MedicalTerm({required this.term, required this.explanation});
}

/// Provides lightweight term matching for inline medical explanations.
class MedicalTerms {
  // This list is intentionally small and local so the frontend can show helpful
  // explanations without waiting for an extra backend lookup.
  static const _terms = [
    MedicalTerm(
      term: 'Anamnese',
      explanation: 'Gezielte Fragen zu Beschwerden, Vorgeschichte und Risiken.',
    ),
    MedicalTerm(
      term: 'Antibiotikum',
      explanation: 'Medikament gegen bestimmte bakterielle Infektionen.',
    ),
    MedicalTerm(
      term: 'Blutdruck',
      explanation: 'Druck des Blutes in den Gefäßen.',
    ),
    MedicalTerm(
      term: 'Dehydrierung',
      explanation: 'Flüssigkeitsmangel im Körper.',
    ),
    MedicalTerm(
      term: 'Entzündung',
      explanation:
          'Reaktion des Körpers, oft mit Schmerz, Wärme, Rötung oder Schwellung.',
    ),
    MedicalTerm(
      term: 'Fieber',
      explanation:
          'Körpertemperatur über 38,0 °C bei Erwachsenen.',
    ),
    MedicalTerm(
      term: 'Infektion',
      explanation:
          'Wenn Erreger wie Viren oder Bakterien in den Körper gelangen.',
    ),
    MedicalTerm(
      term: 'Notfall',
      explanation: 'Situation, in der sofort medizinische Hilfe nötig sein kann.',
    ),
    MedicalTerm(
      term: 'Symptom',
      explanation: 'Ein Zeichen oder eine Beschwerde, die du bemerkst.',
    ),
    MedicalTerm(
      term: 'Therapie',
      explanation:
          'Behandlung, die Beschwerden lindern oder Ursachen angehen soll.',
    ),
    MedicalTerm(
      term: 'Triage',
      explanation:
          'Einschätzung, wie dringend medizinische Hilfe gebraucht wird.',
    ),
  ];

  static List<MedicalTerm> get all => List.unmodifiable(_terms);

  /// Returns the first known glossary term contained in [text], if any.
  static MedicalTerm? firstMatch(String text) {
    final normalized = text.toLowerCase();

    for (final term in _terms) {
      // The current matching is deliberately simple. It favors predictable UI
      // behavior over fuzzy matches that could explain the wrong medical term.
      if (normalized.contains(term.term.toLowerCase())) {
        return term;
      }
    }

    return null;
  }

  const MedicalTerms._();
}
