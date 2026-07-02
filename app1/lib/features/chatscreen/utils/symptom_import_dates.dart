import '../data/models/chat_response_model.dart';
import '../../symptom_diary/data/symptom_import.dart';

List<SymptomImport> buildDatedSymptomImportsFromMessages({
  required List<String> symptoms,
  required List<String> userMessages,
  DateTime? now,
}) {
  final today = _dateOnly(now ?? DateTime.now());
  final imports = <SymptomImport>[];

  for (final symptom in symptoms) {
    // Durations are inclusive: "seit 3 Tagen" means today plus two past days.
    final duration = _durationForSymptom(symptom, userMessages);
    if (duration == null) {
      imports.add(SymptomImport(name: symptom));
      continue;
    }

    for (var daysAgo = duration.daysAgo; daysAgo >= 0; daysAgo--) {
      imports.add(
        SymptomImport(name: symptom, date: _calendarDaysBefore(today, daysAgo)),
      );
    }
  }

  return imports;
}

List<SymptomImport> withObservationSeverity(
  List<SymptomImport> imports,
  List<CaseObservation> observations,
) {
  if (imports.isEmpty || observations.isEmpty) return imports;

  final severitiesByLabel = {
    for (final observation in observations)
      _normalize(observation.label): observation.severity,
  };

  return imports
      .map(
        (symptomImport) => SymptomImport(
          name: symptomImport.name,
          severity:
              symptomImport.severity ??
              severitiesByLabel[_normalize(symptomImport.name)],
          bodyArea: symptomImport.bodyArea,
          date: symptomImport.date,
        ),
      )
      .toList(growable: false);
}

_SymptomDuration? _durationForSymptom(
  String symptom,
  List<String> userMessages,
) {
  final normalizedSymptom = _normalize(symptom);

  for (final message in userMessages.reversed) {
    final normalizedMessage = _normalize(message);
    if (!_messageMentionsSymptom(normalizedMessage, normalizedSymptom)) {
      continue;
    }

    final daysAgo = _extractLastDaysDuration(normalizedMessage);
    if (daysAgo != null) {
      return _SymptomDuration(daysAgo);
    }
  }

  return null;
}

bool _messageMentionsSymptom(String message, String symptom) {
  if (symptom.isEmpty) return false;
  if (message.contains(symptom)) return true;

  final compactMessage = message.replaceAll(' ', '');
  final compactSymptom = symptom.replaceAll(' ', '');
  return compactSymptom.isNotEmpty && compactMessage.contains(compactSymptom);
}

int? _extractLastDaysDuration(String message) {
  final relativeDay = RegExp(
    r'seit\s+(heute|gestern|vorgestern)',
  ).firstMatch(message);
  if (relativeDay != null) {
    return switch (relativeDay.group(1)) {
      'heute' => 0,
      'gestern' => 1,
      'vorgestern' => 2,
      _ => null,
    };
  }

  final match = RegExp(
    r'seit\s+(\d{1,2})\s+tag(?:en|e)?|(?:(?:in|seit)\s+den\s+)?letzten\s+(\d{1,2})\s+tag(?:en|e)?',
  ).firstMatch(message);

  if (match != null) {
    final value = int.tryParse(match.group(1) ?? match.group(2) ?? '');
    if (value == null || value < 1) return null;

    // Cap long spans to one year so chat imports cannot flood the diary dialog.
    return (value - 1).clamp(0, 364);
  }

  final weekMatch = RegExp(
    r'seit\s+(\d{1,2}|ein(?:er|e)?)\s+woch(?:e|en)|(?:(?:in|seit)\s+den\s+)?letzten\s+(\d{1,2})\s+woch(?:e|en)',
  ).firstMatch(message);
  if (weekMatch != null) {
    final weeks = _parseNumber(weekMatch.group(1) ?? weekMatch.group(2));
    if (weeks == null || weeks < 1) return null;

    // Weeks/months/years are approximated into daily diary entries.
    return (weeks * 7 - 1).clamp(0, 364);
  }

  final monthMatch = RegExp(
    r'seit\s+(\d{1,2}|ein(?:em|en)?)\s+monat(?:en|e)?',
  ).firstMatch(message);
  if (monthMatch != null) {
    final months = _parseNumber(monthMatch.group(1));
    if (months == null || months < 1) return null;

    return (months * 30 - 1).clamp(0, 364);
  }

  final yearMatch = RegExp(
    r'seit\s+(?:(\d{1,2}|ein(?:em|en)?)\s+jahr(?:en|e)?|(?:ein(?:em|en)?\s+)?(halbes?|halben|viertel|achtel|ganzes?|ganzen|ganzem)\s+jahr)',
  ).firstMatch(message);
  if (yearMatch != null) {
    final years = _parseNumber(yearMatch.group(1));
    final fractionDays = _fractionalYearDays(yearMatch.group(2));
    final days = years == null ? fractionDays : years * 365;
    if (days == null || days < 1) return null;

    return (days - 1).clamp(0, 364);
  }

  return null;
}

int? _parseNumber(String? value) {
  if (value == null) return null;
  if (value == 'ein' ||
      value == 'eine' ||
      value == 'einer' ||
      value == 'einem' ||
      value == 'einen') {
    return 1;
  }
  return int.tryParse(value);
}

int? _fractionalYearDays(String? value) {
  return switch (value) {
    'halbes' || 'halben' || 'halb' => 183,
    'viertel' => 91,
    'achtel' => 46,
    'ganzes' || 'ganzen' || 'ganzem' || 'ganz' => 365,
    _ => null,
  };
}

DateTime _dateOnly(DateTime value) {
  return DateTime(value.year, value.month, value.day);
}

DateTime _calendarDaysBefore(DateTime today, int daysAgo) {
  // DateTime.subtract uses exact hours, which can land at 23:00 across DST.
  return DateTime(today.year, today.month, today.day - daysAgo);
}

String _normalize(String value) {
  return value
      .toLowerCase()
      .replaceAll('ä', 'ae')
      .replaceAll('ö', 'oe')
      .replaceAll('ü', 'ue')
      .replaceAll('ß', 'ss')
      .replaceAll(RegExp(r'[^a-z0-9]+'), ' ')
      .trim()
      .replaceAll(RegExp(r'\s+'), ' ');
}

class _SymptomDuration {
  final int daysAgo;

  const _SymptomDuration(this.daysAgo);
}
