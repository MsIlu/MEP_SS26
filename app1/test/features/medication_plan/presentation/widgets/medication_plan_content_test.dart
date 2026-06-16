import 'package:app1/features/medication_plan/data/medication_entry.dart';
import 'package:app1/features/medication_plan/presentation/widgets/layout/medication_plan_content.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  // Test case references: documents/Testfaelle_Frontend_Aufgaben.md#t01-medicationbook
  group('MedicationPlanContent', () {
    testWidgets('renders the page title and bottom medication actions', (
      WidgetTester tester,
    ) async {
      await tester.pumpWidget(
        _TestShell(
          child: MedicationPlanContent(
            selectedDate: DateTime(2026, 6, 2),
            today: DateTime(2026, 6, 2),
            entries: const [],
            onDateSelected: (_) {},
            onOpenMedicationList: () {},
            onAddMedication: () {},
            onTakenChanged: (_, _, _, _) {},
          ),
        ),
      );

      expect(find.text('Meine Medikamente'), findsOneWidget);
      expect(find.byTooltip('Medikament hinzufügen'), findsOneWidget);
    });

    testWidgets('calls bottom action callbacks', (WidgetTester tester) async {
      // The bottom actions are the primary entry points for editing medication.
      var openedMedicationList = false;
      var openedMedicationForm = false;
      await tester.pumpWidget(
        _TestShell(
          child: MedicationPlanContent(
            selectedDate: DateTime(2026, 6, 2),
            today: DateTime(2026, 6, 2),
            entries: [_entry()],
            onDateSelected: (_) {},
            onOpenMedicationList: () {
              openedMedicationList = true;
            },
            onAddMedication: () {
              openedMedicationForm = true;
            },
            onTakenChanged: (_, _, _, _) {},
          ),
        ),
      );

      await tester.tap(find.text('Meine Medikamente'));
      await tester.tap(find.byTooltip('Medikament hinzufügen'));

      expect(openedMedicationList, isTrue);
      expect(openedMedicationForm, isTrue);
    });
  });
}

class _TestShell extends StatelessWidget {
  final Widget child;

  const _TestShell({required this.child});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(home: Scaffold(body: child));
  }
}

MedicationEntry _entry() {
  return MedicationEntry(
    id: 1,
    name: 'Ibuprofen',
    dose: '400 mg',
    intakeTime: const TimeOfDay(hour: 8, minute: 0),
    remindersEnabled: true,
    createdAt: DateTime(2026, 6, 2),
  );
}
