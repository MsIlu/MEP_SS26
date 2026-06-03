import 'package:app1/features/medication_plan/data/medication_entry.dart';
import 'package:app1/features/medication_plan/data/medication_schedule.dart';
import 'package:app1/features/medication_plan/presentation/utils/medication_date_format.dart';
import 'package:app1/features/medication_plan/presentation/widgets/daily_plan/medication_daily_plan_section.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('MedicationDailyPlanSection', () {
    testWidgets('shows the selected day doses with 24-hour times', (
      WidgetTester tester,
    ) async {
      final today = DateTime(2026, 6, 2);
      final entry = _entry(
        frequency: MedicationFrequency.twiceDaily,
        secondIntakeTime: const TimeOfDay(hour: 20, minute: 0),
      );

      await tester.pumpWidget(
        _TestShell(
          child: MedicationDailyPlanSection(
            selectedDate: today,
            today: today,
            entries: [entry],
            onTakenChanged: (_, _, _, _) {},
          ),
        ),
      );

      expect(find.text('Heute geplant'), findsOneWidget);
      expect(find.text('08:00 Uhr'), findsOneWidget);
      expect(find.text('20:00 Uhr'), findsOneWidget);
      expect(find.text('400 mg - Einnahme 1'), findsOneWidget);
      expect(find.text('400 mg - Einnahme 2'), findsOneWidget);
    });

    testWidgets('disables taken checkbox for future days', (
      WidgetTester tester,
    ) async {
      // Future intake state must not be editable from the daily plan.
      var wasChanged = false;

      await tester.pumpWidget(
        _TestShell(
          child: MedicationDailyPlanSection(
            selectedDate: DateTime(2026, 6, 3),
            today: DateTime(2026, 6, 2),
            entries: [_entry()],
            onTakenChanged: (_, _, _, _) {
              wasChanged = true;
            },
          ),
        ),
      );

      final checkbox = tester.widget<Checkbox>(find.byType(Checkbox));

      expect(checkbox.onChanged, isNull);
      await tester.tap(find.text('Eingenommen'));
      await tester.pump();
      expect(wasChanged, isFalse);
    });

    testWidgets('renders taken doses without hiding their text', (
      WidgetTester tester,
    ) async {
      final today = DateTime(2026, 6, 2);
      final takenEntry = _entry(
        takenDateKeys: [medicationDoseDateKey(today, 0)],
      );

      await tester.pumpWidget(
        _TestShell(
          child: MedicationDailyPlanSection(
            selectedDate: today,
            today: today,
            entries: [takenEntry],
            onTakenChanged: (_, _, _, _) {},
          ),
        ),
      );

      expect(find.text('Ibuprofen'), findsOneWidget);
      expect(find.text('400 mg'), findsOneWidget);
      expect(tester.widget<Checkbox>(find.byType(Checkbox)).value, isTrue);
    });
  });
}

class _TestShell extends StatelessWidget {
  final Widget child;

  const _TestShell({required this.child});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(body: Center(child: child)),
    );
  }
}

MedicationEntry _entry({
  MedicationFrequency frequency = MedicationFrequency.daily,
  TimeOfDay intakeTime = const TimeOfDay(hour: 8, minute: 0),
  TimeOfDay? secondIntakeTime,
  List<String> takenDateKeys = const [],
}) {
  return MedicationEntry(
    id: 1,
    name: 'Ibuprofen',
    dose: '400 mg',
    intakeTime: intakeTime,
    secondIntakeTime: secondIntakeTime,
    frequency: frequency,
    remindersEnabled: true,
    createdAt: DateTime(2026, 6, 2),
    takenDateKeys: takenDateKeys,
  );
}
