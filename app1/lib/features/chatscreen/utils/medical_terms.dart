class MedicalTerm {
  final String term;
  final String explanation;

  const MedicalTerm({required this.term, required this.explanation});
}

class MedicalTerms {
  static const _terms = [
    MedicalTerm(
      term: 'Symptom',
      explanation: 'Ein Zeichen oder eine Beschwerde, die du bemerkst.',
    ),
    MedicalTerm(
      term: 'Entzündung',
      explanation:
          'Reaktion des Körpers, oft mit Schmerz, Wärme, Rötung oder Schwellung.',
    ),
    MedicalTerm(
      term: 'Infektion',
      explanation:
          'Wenn Erreger wie Viren oder Bakterien in den Körper gelangen.',
    ),
    MedicalTerm(
      term: 'Therapie',
      explanation:
          'Behandlung, die Beschwerden lindern oder Ursachen angehen soll.',
    ),
  ];

  static MedicalTerm? firstMatch(String text) {
    final normalized = text.toLowerCase();

    for (final term in _terms) {
      if (normalized.contains(term.term)) {
        return term;
      }
    }

    return null;
  }

  const MedicalTerms._();
}