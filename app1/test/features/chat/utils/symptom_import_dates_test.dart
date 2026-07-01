import 'package:app1/features/chatscreen/utils/symptom_import_dates.dart';
import 'package:app1/features/chatscreen/data/models/chat_response_model.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('expands symptoms with a numeric duration into dated imports', () {
    final imports = buildDatedSymptomImportsFromMessages(
      symptoms: const ['Halsschmerzen'],
      userMessages: const [
        'Seit 3 Tagen habe ich Halsschmerzen',
      ],
      now: DateTime(2026, 7, 1, 14),
    );

    expect(imports.map((symptomImport) => symptomImport.name), [
      'Halsschmerzen',
      'Halsschmerzen',
      'Halsschmerzen',
    ]);
    expect(imports.map((symptomImport) => symptomImport.date), [
      DateTime(2026, 6, 29),
      DateTime(2026, 6, 30),
      DateTime(2026, 7, 1),
    ]);
  });

  test('keeps a symptom undated when no duration was mentioned', () {
    final imports = buildDatedSymptomImportsFromMessages(
      symptoms: const ['Kopfschmerzen'],
      userMessages: const ['Ich habe Kopfschmerzen'],
      now: DateTime(2026, 7, 1),
    );

    expect(imports, hasLength(1));
    expect(imports.single.name, 'Kopfschmerzen');
    expect(imports.single.date, isNull);
  });

  test('uses duration only for symptoms mentioned in the same message', () {
    final imports = buildDatedSymptomImportsFromMessages(
      symptoms: const ['Husten', 'Bauchschmerzen'],
      userMessages: const ['Seit 3 Tagen habe ich Bauchschmerzen'],
      now: DateTime(2026, 7, 1),
    );

    final cough = imports.firstWhere(
      (symptomImport) => symptomImport.name == 'Husten',
    );
    final bellyPain = imports
        .where((symptomImport) => symptomImport.name == 'Bauchschmerzen')
        .toList();

    expect(cough.date, isNull);
    expect(bellyPain, hasLength(3));
    expect(bellyPain.first.date, DateTime(2026, 6, 29));
  });

  test('uses the latest matching user message for a symptom duration', () {
    final imports = buildDatedSymptomImportsFromMessages(
      symptoms: const ['Husten'],
      userMessages: const [
        'Seit 5 Tagen habe ich Husten',
        'Seit gestern ist der Husten stärker',
      ],
      now: DateTime(2026, 7, 1),
    );

    expect(imports, hasLength(2));
    expect(imports.map((symptomImport) => symptomImport.date), [
      DateTime(2026, 6, 30),
      DateTime(2026, 7, 1),
    ]);
  });

  test('expands symptoms mentioned since relative days', () {
    final sinceYesterday = buildDatedSymptomImportsFromMessages(
      symptoms: const ['Husten'],
      userMessages: const ['Seit gestern habe ich Husten'],
      now: DateTime(2026, 7, 1),
    );
    final sinceTheDayBeforeYesterday = buildDatedSymptomImportsFromMessages(
      symptoms: const ['Schnupfen'],
      userMessages: const ['Seit vorgestern habe ich Schnupfen'],
      now: DateTime(2026, 7, 1),
    );
    final sinceToday = buildDatedSymptomImportsFromMessages(
      symptoms: const ['Fieber'],
      userMessages: const ['Seit heute habe ich Fieber'],
      now: DateTime(2026, 7, 1),
    );

    expect(sinceYesterday.map((symptomImport) => symptomImport.date), [
      DateTime(2026, 6, 30),
      DateTime(2026, 7, 1),
    ]);
    expect(
      sinceTheDayBeforeYesterday.map((symptomImport) => symptomImport.date),
      [
        DateTime(2026, 6, 29),
        DateTime(2026, 6, 30),
        DateTime(2026, 7, 1),
      ],
    );
    expect(sinceToday.map((symptomImport) => symptomImport.date), [
      DateTime(2026, 7, 1),
    ]);
  });

  test('expands week durations into daily imports', () {
    final twoWeeks = buildDatedSymptomImportsFromMessages(
      symptoms: const ['Ohrenschmerzen'],
      userMessages: const ['Seit 2 Wochen habe ich Ohrenschmerzen'],
      now: DateTime(2026, 7, 1),
    );
    final oneWeek = buildDatedSymptomImportsFromMessages(
      symptoms: const ['Juckreiz'],
      userMessages: const ['Seit einer Woche habe ich Juckreiz'],
      now: DateTime(2026, 7, 1),
    );
    final lastThreeWeeks = buildDatedSymptomImportsFromMessages(
      symptoms: const ['Ausschlag'],
      userMessages: const ['In den letzten 3 Wochen hatte ich Ausschlag'],
      now: DateTime(2026, 7, 1),
    );

    expect(twoWeeks, hasLength(14));
    expect(twoWeeks.first.date, DateTime(2026, 6, 18));
    expect(twoWeeks.last.date, DateTime(2026, 7, 1));
    expect(oneWeek, hasLength(7));
    expect(oneWeek.first.date, DateTime(2026, 6, 25));
    expect(lastThreeWeeks, hasLength(21));
    expect(lastThreeWeeks.first.date, DateTime(2026, 6, 11));
  });

  test('expands month and year durations with a one year cap', () {
    final oneMonth = buildDatedSymptomImportsFromMessages(
      symptoms: const ['Nackenschmerzen'],
      userMessages: const ['Seit einem Monat habe ich Nackenschmerzen'],
      now: DateTime(2026, 7, 1),
    );
    final sixMonths = buildDatedSymptomImportsFromMessages(
      symptoms: const ['Rückenschmerzen'],
      userMessages: const ['Seit 6 Monaten habe ich Rückenschmerzen'],
      now: DateTime(2026, 7, 1),
    );
    final halfYear = buildDatedSymptomImportsFromMessages(
      symptoms: const ['Schwindel'],
      userMessages: const ['Seit einem halben Jahr habe ich Schwindel'],
      now: DateTime(2026, 7, 1),
    );
    final quarterYear = buildDatedSymptomImportsFromMessages(
      symptoms: const ['Übelkeit'],
      userMessages: const ['Seit einem viertel Jahr habe ich Übelkeit'],
      now: DateTime(2026, 7, 1),
    );
    final eighthYear = buildDatedSymptomImportsFromMessages(
      symptoms: const ['Augenbrennen'],
      userMessages: const ['Seit einem achtel Jahr habe ich Augenbrennen'],
      now: DateTime(2026, 7, 1),
    );
    final wholeYear = buildDatedSymptomImportsFromMessages(
      symptoms: const ['Müdigkeit'],
      userMessages: const ['Seit einem ganzen Jahr habe ich Müdigkeit'],
      now: DateTime(2026, 7, 1),
    );
    final longDuration = buildDatedSymptomImportsFromMessages(
      symptoms: const ['Schmerzen'],
      userMessages: const ['Seit 99 Wochen habe ich Schmerzen'],
      now: DateTime(2026, 7, 1),
    );

    expect(oneMonth, hasLength(30));
    expect(sixMonths, hasLength(180));
    expect(sixMonths.first.date, DateTime(2026, 1, 3));
    expect(sixMonths.last.date, DateTime(2026, 7, 1));
    expect(halfYear, hasLength(183));
    expect(quarterYear, hasLength(91));
    expect(eighthYear, hasLength(46));
    expect(wholeYear, hasLength(365));
    expect(longDuration, hasLength(365));
    expect(longDuration.first.date, DateTime(2025, 7, 2));
  });

  test('keeps unsupported or invalid durations undated', () {
    final zeroDays = buildDatedSymptomImportsFromMessages(
      symptoms: const ['Husten'],
      userMessages: const ['Seit 0 Tagen habe ich Husten'],
      now: DateTime(2026, 7, 1),
    );
    final wordNumber = buildDatedSymptomImportsFromMessages(
      symptoms: const ['Fieber'],
      userMessages: const ['Seit drei Tagen habe ich Fieber'],
      now: DateTime(2026, 7, 1),
    );

    expect(zeroDays.single.date, isNull);
    expect(wordNumber.single.date, isNull);
  });

  test('matches symptoms with umlaut transliteration', () {
    final imports = buildDatedSymptomImportsFromMessages(
      symptoms: const ['Übelkeit'],
      userMessages: const ['Seit gestern habe ich uebelkeit'],
      now: DateTime(2026, 7, 1),
    );

    expect(imports, hasLength(2));
    expect(imports.first.date, DateTime(2026, 6, 30));
  });

  test('adds matching observation severity without changing import dates', () {
    final imports = buildDatedSymptomImportsFromMessages(
      symptoms: const ['Bauchschmerzen'],
      userMessages: const ['Seit den letzten 2 Tagen Bauchschmerzen'],
      now: DateTime(2026, 7, 1),
    );

    final enriched = withObservationSeverity(imports, const [
      CaseObservation(label: 'Bauchschmerzen', severity: 6),
    ]);

    expect(enriched.map((symptomImport) => symptomImport.severity), [6, 6, 6]);
    expect(enriched.map((symptomImport) => symptomImport.date), [
      DateTime(2026, 6, 29),
      DateTime(2026, 6, 30),
      DateTime(2026, 7, 1),
    ]);
  });
}
