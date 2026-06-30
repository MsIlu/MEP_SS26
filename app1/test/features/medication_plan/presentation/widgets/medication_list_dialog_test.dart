import 'package:app1/features/medication_plan/data/medication_entry.dart';
import 'package:app1/features/medication_plan/presentation/widgets/list/medication_list_dialog.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('MedicationListDialog', () {
    testWidgets('calls edit callback for a saved medication', (
      WidgetTester tester,
    ) async {
      MedicationEntry? editedEntry;

      await tester.pumpWidget(
        _TestShell(
          child: MedicationListDialog(
            isLoading: false,
            entries: [_entry()],
            onAdd: () {},
            onClose: () {},
            onToggleReminder: (_, _) {},
            onEdit: (entry) {
              editedEntry = entry;
            },
            onDelete: (_) {},
          ),
        ),
      );

      await tester.tap(find.byTooltip('Ibuprofen bearbeiten'));

      expect(editedEntry?.name, 'Ibuprofen');
    });
  });
}

class _TestShell extends StatelessWidget {
  final Widget child;

  const _TestShell({required this.child});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        body: Center(child: SizedBox(width: 420, height: 360, child: child)),
      ),
    );
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
