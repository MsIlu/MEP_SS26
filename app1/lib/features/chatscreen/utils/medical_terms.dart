/// Small glossary entry used to explain medical language inside chat replies.
class MedicalTerm {
  /// Word or phrase that should be detected in a response.
  final String term;

  /// Plain-language explanation shown to the user.
  final String explanation;

  /// Additional words that should also find this entry in search or chat text.
  final List<String> aliases;

  const MedicalTerm({
    required this.term,
    required this.explanation,
    this.aliases = const [],
  });

  bool matchesQuery(String query) {
    if (query.isEmpty) {
      return true;
    }

    final normalizedQuery = query.toLowerCase();
    return '$term $explanation ${aliases.join(' ')}'.toLowerCase().contains(
      normalizedQuery,
    );
  }
}

/// Provides lightweight term matching for inline medical explanations.
class MedicalTerms {
  static const List<MedicalTerm> terms = [
    MedicalTerm(
      term: 'Akut',
      explanation: 'Plötzlich beginnend oder erst seit kurzer Zeit vorhanden.',
    ),
    MedicalTerm(
      term: 'Anamnese',
      explanation:
          'Die Vorgeschichte und Angaben zu Beschwerden, Erkrankungen und Medikamenten.',
    ),
    MedicalTerm(
      term: 'Atemnot',
      explanation:
          'Das Gefühl, nicht genug Luft zu bekommen oder schwer atmen zu können.',
      aliases: ['Dyspnoe'],
    ),
    MedicalTerm(
      term: 'Chronisch',
      explanation: 'Über längere Zeit bestehend oder immer wiederkehrend.',
    ),
    MedicalTerm(
      term: 'Dehydrierung',
      explanation:
          'Flüssigkeitsmangel im Körper, zum Beispiel durch Fieber, Durchfall oder Erbrechen.',
    ),
    MedicalTerm(
      term: 'Diagnose',
      explanation:
          'Ärztliche Einordnung, welche Erkrankung oder Ursache wahrscheinlich vorliegt.',
    ),
    MedicalTerm(
      term: 'Entzündung',
      explanation:
          'Reaktion des Körpers, oft mit Schmerz, Wärme, Rötung oder Schwellung.',
    ),
    MedicalTerm(
      term: 'Fieber',
      explanation:
          'Erhöhte Körpertemperatur; bei Erwachsenen meist ab über 38,0 °C.',
    ),
    MedicalTerm(
      term: 'Infektion',
      explanation:
          'Wenn Erreger wie Viren oder Bakterien in den Körper gelangen und Beschwerden auslösen können.',
    ),
    MedicalTerm(
      term: 'Kreislauf',
      explanation:
          'Das Zusammenspiel von Herz, Blutgefäßen und Blutdruck, das den Körper versorgt.',
    ),
    MedicalTerm(
      term: 'Medikation',
      explanation:
          'Die Medikamente, die eine Person einnimmt oder einnehmen soll.',
      aliases: ['Medikamente'],
    ),
    MedicalTerm(
      term: 'Ödem',
      explanation: 'Eine Schwellung durch Flüssigkeitseinlagerung im Gewebe.',
      aliases: ['Oedem', 'Wassereinlagerung'],
    ),
    MedicalTerm(
      term: 'Prognose',
      explanation:
          'Einschätzung, wie sich Beschwerden oder eine Erkrankung weiterentwickeln könnten.',
    ),
    MedicalTerm(
      term: 'Red Flag',
      explanation:
          'Warnzeichen, bei dem medizinisch rasch abgeklärt werden sollte, ob etwas Ernstes vorliegt.',
      aliases: ['Warnzeichen'],
    ),
    MedicalTerm(
      term: 'Symptom',
      explanation: 'Ein Zeichen oder eine Beschwerde, die du bemerkst.',
    ),
    MedicalTerm(
      term: 'Synkope',
      explanation:
          'Kurzzeitige Ohnmacht oder Bewusstlosigkeit, meist durch vorübergehend zu wenig Blutfluss zum Gehirn.',
      aliases: ['Ohnmacht'],
    ),
    MedicalTerm(
      term: 'Therapie',
      explanation:
          'Behandlung, die Beschwerden lindern oder Ursachen angehen soll.',
    ),
    MedicalTerm(
      term: 'Trauma',
      explanation:
          'Verletzung oder körperliche Belastung durch ein äußeres Ereignis, zum Beispiel einen Sturz.',
    ),
    MedicalTerm(
      term: 'Vitalzeichen',
      explanation:
          'Messwerte wie Puls, Blutdruck, Temperatur und Atmung, die den Zustand des Körpers zeigen.',
    ),
  ];

  static List<MedicalTerm> search(String query) {
    final normalizedQuery = query.trim().toLowerCase();
    return terms
        .where((term) => term.matchesQuery(normalizedQuery))
        .toList(growable: false);
  }

  /// Returns the first known glossary term contained in [text], if any.
  static MedicalTerm? firstMatch(String text) {
    final matches = matchesIn(text);
    return matches.isEmpty ? null : matches.first.term;
  }

  static List<MedicalTermMatch> matchesIn(String text) {
    final normalized = text.toLowerCase();
    final matches = <MedicalTermMatch>[];

    for (final term in terms) {
      for (final candidate in [term.term, ...term.aliases]) {
        final normalizedCandidate = candidate.toLowerCase();
        var start = 0;

        while (start < normalized.length) {
          final index = normalized.indexOf(normalizedCandidate, start);
          if (index == -1) {
            break;
          }

          final end = index + normalizedCandidate.length;
          if (_hasWordBoundaries(normalized, index, end) &&
              !_overlaps(matches, index, end)) {
            matches.add(MedicalTermMatch(term: term, start: index, end: end));
          }

          start = end;
        }
      }
    }

    matches.sort((first, second) => first.start.compareTo(second.start));
    return matches;
  }

  static bool _overlaps(List<MedicalTermMatch> matches, int start, int end) {
    return matches.any((match) => start < match.end && end > match.start);
  }

  static bool _hasWordBoundaries(String text, int start, int end) {
    final before = start == 0 ? null : text[start - 1];
    final after = end >= text.length ? null : text[end];
    return !_isWordCharacter(before) && !_isWordCharacter(after);
  }

  static bool _isWordCharacter(String? value) {
    if (value == null) {
      return false;
    }

    final rune = value.runes.first;
    return (rune >= 48 && rune <= 57) ||
        (rune >= 65 && rune <= 90) ||
        (rune >= 97 && rune <= 122) ||
        rune == 95 ||
        rune >= 0x00C0;
  }

  const MedicalTerms._();
}

class MedicalTermMatch {
  final MedicalTerm term;
  final int start;
  final int end;

  const MedicalTermMatch({
    required this.term,
    required this.start,
    required this.end,
  });
}
