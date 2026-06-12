import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:app1/features/chatscreen/presentation/widgets/symptom_list.dart';

void main() {
  testWidgets('shows symptom chips when symptoms exist', (tester) async {
    final symptoms = ValueNotifier<List<String>>([
      'Kopfschmerzen',
      'Uebelkeit',
    ]);

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: SymptomList(
            symptomsListenable: symptoms,
            onAddPressed: () {},
            onSymptomPressed: (_) {},
          ),
        ),
      ),
    );

    expect(find.text('Erkannte Symptome:'), findsOneWidget);
    expect(find.text('Bearbeiten'), findsOneWidget);
    expect(find.text('Kopfschmerzen'), findsOneWidget);
    expect(find.text('Uebelkeit'), findsOneWidget);
  });

  testWidgets('hides symptom list when no symptoms exist', (tester) async {
    final symptoms = ValueNotifier<List<String>>([]);

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: SymptomList(
            symptomsListenable: symptoms,
            onAddPressed: () {},
            onSymptomPressed: (_) {},
          ),
        ),
      ),
    );

    expect(find.text('Erkannte Symptome:'), findsNothing);
    expect(find.text('Bearbeiten'), findsNothing);
  });

  testWidgets('groups hidden symptoms when more than three exist', (
    tester,
  ) async {
    final symptoms = ValueNotifier<List<String>>([
      'Kopfschmerzen',
      'Uebelkeit',
      'Schwindel',
      'Fieber',
      'Husten',
    ]);

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: SymptomList(
            symptomsListenable: symptoms,
            onAddPressed: () {},
            onSymptomPressed: (_) {},
          ),
        ),
      ),
    );

    expect(find.text('Kopfschmerzen'), findsOneWidget);
    expect(find.text('Uebelkeit'), findsOneWidget);
    expect(find.text('Schwindel'), findsOneWidget);
    expect(find.text('+2'), findsOneWidget);
    expect(find.text('Fieber'), findsNothing);
    expect(find.text('Husten'), findsNothing);
  });

  testWidgets('truncates long symptom labels visually', (tester) async {
    const longSymptom = 'Desoxyribonucleinsaeureunvertraeglichkeit';
    final symptoms = ValueNotifier<List<String>>([longSymptom]);
    String? selectedSymptom;

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: SymptomList(
            symptomsListenable: symptoms,
            onAddPressed: () {},
            onSymptomPressed: (symptom) {
              selectedSymptom = symptom;
            },
          ),
        ),
      ),
    );

    final label = tester.widget<Text>(find.text(longSymptom));

    expect(label.maxLines, 1);
    expect(label.overflow, TextOverflow.ellipsis);
    expect(label.softWrap, false);

    await tester.tap(find.text(longSymptom));

    expect(selectedSymptom, longSymptom);
  });
}
