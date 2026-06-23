import 'package:app1/core/themes/theme_controller.dart';
import 'package:app1/features/symptom_diary/data/symptom_entry.dart';
import 'package:app1/features/symptom_diary/presentation/screens/symptom_diary_page.dart';
import 'package:app1/features/symptom_diary/presentation/widgets/body_area_selector.dart';
import 'package:app1/features/symptom_diary/presentation/widgets/symptom_diary_content.dart';
import 'package:app1/features/symptom_diary/presentation/widgets/symptom_entry_form.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  group('Symptom diary UI', () {
    setUp(() {
      SharedPreferences.setMockInitialValues({});
    });

    testWidgets('renders the full page and saves a local entry', (
      tester,
    ) async {
      final themeController = ThemeController();
      addTearDown(themeController.dispose);

      await tester.pumpWidget(
        MaterialApp(
          home: SymptomDiaryPage(themeController: themeController),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Symptomtagebuch'), findsOneWidget);
      expect(find.text('Noch nichts eingetragen'), findsOneWidget);

      await tester.tap(find.byTooltip('Symptom eintragen'));
      await tester.pumpAndSettle();

      await tester.enterText(find.byType(TextField), 'Husten');
      await tester.tap(find.text('Weiter'));
      await tester.pumpAndSettle();

      await tester.enterText(find.byType(TextField), 'Seit gestern Abend');
      await tester.tap(find.text('Speichern'));
      await tester.pumpAndSettle();

      expect(find.text('Symptom gespeichert'), findsOneWidget);
      expect(find.text('Husten'), findsWidgets);

      await tester.tap(find.byTooltip('Lightmode aktivieren'));
      await tester.pump();

      expect(themeController.isDarkMode, isFalse);
    });

    testWidgets('selects and clears a body area from chips', (tester) async {
      var selectedArea = '';

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: StatefulBuilder(
              builder: (context, setState) {
                return BodyAreaSelector(
                  selectedArea: selectedArea,
                  onChanged: (area) => setState(() => selectedArea = area),
                );
              },
            ),
          ),
        ),
      );

      expect(find.text('optional'), findsOneWidget);

      await tester.tap(find.widgetWithText(ChoiceChip, 'Kopf'));
      await tester.pump();

      expect(selectedArea, 'Kopf');
      expect(find.text('Kopf'), findsWidgets);

      await tester.tap(find.widgetWithText(ChoiceChip, 'Kopf'));
      await tester.pump();

      expect(selectedArea, isEmpty);
      expect(find.text('optional'), findsOneWidget);
    });

    testWidgets('selects a body area from the body image', (tester) async {
      var selectedArea = '';

      await tester.binding.setSurfaceSize(const Size(420, 800));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Center(
              child: SizedBox(
                width: 360,
                child: BodyAreaSelector(
                  selectedArea: selectedArea,
                  onChanged: (area) => selectedArea = area,
                ),
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      final bodyImageGesture = find.ancestor(
        of: find.byType(CustomPaint),
        matching: find.byType(GestureDetector),
      );
      expect(bodyImageGesture, findsOneWidget);

      final gestureRect = tester.getRect(bodyImageGesture);
      await tester.tapAt(
        gestureRect.topLeft + Offset(gestureRect.width / 2, 35),
      );
      await tester.pump();

      expect(selectedArea, 'Kopf');
    });

    testWidgets('shows empty day state and opens add action', (tester) async {
      var addPressed = false;
      final today = DateTime(2026, 6, 22);

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SizedBox(
              height: 700,
              child: SymptomDiaryContent(
                selectedDate: today,
                today: today,
                isLoading: false,
                entries: const [],
                allEntries: const [],
                onDateSelected: (_) {},
                onAddSymptom: () => addPressed = true,
                onDelete: (_) {},
              ),
            ),
          ),
        ),
      );

      expect(find.text('Noch nichts eingetragen'), findsOneWidget);
      expect(find.textContaining('Noch keine Symptome'), findsOneWidget);

      await tester.tap(find.byTooltip('Symptom eintragen'));
      await tester.pump();

      expect(addPressed, isTrue);
    });

    testWidgets('saves symptom entry from the form', (tester) async {
      final savedEntries = <_SavedSymptom>[];
      var savedCallbackCalled = false;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SingleChildScrollView(
              child: SymptomEntryForm(
                onSave: ({
                  required symptom,
                  required bodyArea,
                  required intensity,
                  required note,
                }) async {
                  savedEntries.add(
                    _SavedSymptom(
                      symptom: symptom,
                      bodyArea: bodyArea,
                      intensity: intensity,
                      note: note,
                    ),
                  );
                },
                onSaved: () => savedCallbackCalled = true,
              ),
            ),
          ),
        ),
      );

      await tester.enterText(find.byType(TextField), 'Husten');
      await tester.tap(find.text('Weiter'));
      await tester.pumpAndSettle();

      await tester.enterText(find.byType(TextField), 'Seit gestern Abend');
      await tester.tap(find.text('Speichern'));
      await tester.pumpAndSettle();

      expect(savedEntries, hasLength(1));
      expect(savedEntries.single.symptom, 'Husten');
      expect(savedEntries.single.bodyArea, '');
      expect(savedEntries.single.intensity, 5);
      expect(savedEntries.single.note, 'Seit gestern Abend');
      expect(savedCallbackCalled, isTrue);
    });

    testWidgets('renders existing entry and calls delete', (tester) async {
      final today = DateTime(2026, 6, 22);
      final entry = SymptomEntry(
        id: 1,
        date: today,
        symptom: 'Husten',
        intensity: 6,
        note: 'Nach dem Sport',
        createdAt: DateTime(2026, 6, 22, 9),
      );
      SymptomEntry? deletedEntry;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SizedBox(
              height: 700,
              child: SymptomDiaryContent(
                selectedDate: today,
                today: today,
                isLoading: false,
                entries: [entry],
                allEntries: [entry],
                onDateSelected: (_) {},
                onAddSymptom: () {},
                onDelete: (entry) => deletedEntry = entry,
              ),
            ),
          ),
        ),
      );

      expect(find.text('1 Einträge für diesen Tag'), findsOneWidget);
      expect(find.text('Husten'), findsWidgets);
      expect(find.text('Nach dem Sport'), findsOneWidget);

      await tester.tap(find.byIcon(Icons.delete_outline));
      await tester.pump();

      expect(deletedEntry, same(entry));
    });
  });
}

class _SavedSymptom {
  final String symptom;
  final String bodyArea;
  final int intensity;
  final String note;

  const _SavedSymptom({
    required this.symptom,
    required this.bodyArea,
    required this.intensity,
    required this.note,
  });
}
