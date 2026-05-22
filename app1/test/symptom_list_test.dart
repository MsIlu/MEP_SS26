import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:app1/features/chat/presentation/widgets/symptom_list.dart';

void main() {
  testWidgets('shows symptom bubbles when symptoms exist', (tester) async {
    final symptoms = ValueNotifier<List<String>>([
      'Kopfschmerzen',
      'Übelkeit',
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
    expect(find.text('Übelkeit'), findsOneWidget);
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

  testWidgets('shows hidden symptom count when more than three symptoms exist',
          (tester) async {
        final symptoms = ValueNotifier<List<String>>([
          'Kopfschmerzen',
          'Übelkeit',
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
        expect(find.text('Übelkeit'), findsOneWidget);
        expect(find.text('Schwindel'), findsOneWidget);
        expect(find.text('+2'), findsOneWidget);

        expect(find.text('Fieber'), findsNothing);
        expect(find.text('Husten'), findsNothing);
      });
}