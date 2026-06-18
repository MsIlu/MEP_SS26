import 'package:app1/features/appointmentscreen/controllers/appointment_controller.dart';
import 'package:app1/features/appointmentscreen/presentation/screens/appointment_screen.dart';
import 'package:app1/features/appointmentscreen/data/models/appointment.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  late AppointmentController controller;

  setUp(() {
    controller = AppointmentController();
    controller.appointments.value = [];
  });

  Future<void> pumpAppointmentScreen(WidgetTester tester) async {
    await tester.binding.setSurfaceSize(const Size(800, 900));

    await tester.pumpWidget(const MaterialApp(home: AppointmentScreen()));

    await tester.pumpAndSettle();
  }

  tearDown(() {
    controller.appointments.value = [];
  });

  testWidgets('shows empty state when no appointments exist', (tester) async {
    await pumpAppointmentScreen(tester);

    expect(find.text('Noch keine Termine vorhanden'), findsOneWidget);
    expect(find.text('Deine Termine'), findsOneWidget);
  });

  testWidgets('opens add appointment dialog', (tester) async {
    await pumpAppointmentScreen(tester);

    await tester.tap(find.byIcon(Icons.add));
    await tester.pumpAndSettle();

    expect(find.text('Termin hinzufügen'), findsOneWidget);
    expect(find.text('Arzt'), findsOneWidget);
    expect(find.text('Datum'), findsOneWidget);
    expect(find.text('Uhrzeit'), findsOneWidget);
    expect(find.text('Notiz (optional)'), findsOneWidget);
    expect(find.text('Abbrechen'), findsOneWidget);
    expect(find.text('Speichern'), findsOneWidget);
  });

  testWidgets('cancel clears entered appointment data', (tester) async {
    await pumpAppointmentScreen(tester);

    await tester.tap(find.byIcon(Icons.add));
    await tester.pumpAndSettle();

    final doctorField = find.byWidgetPredicate(
      (widget) => widget is TextField && widget.decoration?.labelText == 'Arzt',
    );

    final noteField = find.byWidgetPredicate(
      (widget) =>
          widget is TextField &&
          widget.decoration?.labelText == 'Notiz (optional)',
    );

    await tester.enterText(doctorField, 'Hausarzt');
    await tester.enterText(noteField, 'Kontrolltermin');

    await tester.tap(find.text('Abbrechen'));
    await tester.pumpAndSettle();

    expect(find.text('Termin hinzufügen'), findsNothing);

    await tester.tap(find.byIcon(Icons.add));
    await tester.pumpAndSettle();

    final reopenedDoctorField = tester.widget<TextField>(doctorField);
    final reopenedNoteField = tester.widget<TextField>(noteField);

    expect(reopenedDoctorField.controller?.text, isEmpty);
    expect(reopenedNoteField.controller?.text, isEmpty);
  });

  testWidgets(
    'does not save appointment without doctor when date and time are set',
    (tester) async {
      await pumpAppointmentScreen(tester);

      await tester.tap(find.byIcon(Icons.add));
      await tester.pumpAndSettle();

      final dateField = find.byWidgetPredicate(
        (widget) =>
            widget is TextField && widget.decoration?.labelText == 'Datum',
      );

      final timeField = find.byWidgetPredicate(
        (widget) =>
            widget is TextField && widget.decoration?.labelText == 'Uhrzeit',
      );

      await tester.tap(dateField);
      await tester.pumpAndSettle();
      await tester.tap(find.text('OK'));
      await tester.pumpAndSettle();

      await tester.tap(timeField);
      await tester.pumpAndSettle();
      await tester.tap(find.text('OK'));
      await tester.pumpAndSettle();

      expect(tester.widget<TextField>(dateField).controller?.text, isNotEmpty);
      expect(tester.widget<TextField>(timeField).controller?.text, isNotEmpty);

      await tester.tap(find.text('Speichern'));
      await tester.pumpAndSettle();

      expect(controller.appointments.value, isEmpty);

      expect(find.text('Termin hinzufügen'), findsOneWidget);
    },
  );

  testWidgets('saves and displays a valid appointment', (tester) async {
    await pumpAppointmentScreen(tester);

    await tester.tap(find.byIcon(Icons.add));
    await tester.pumpAndSettle();

    final doctorField = find.byWidgetPredicate(
      (widget) => widget is TextField && widget.decoration?.labelText == 'Arzt',
    );

    final dateField = find.byWidgetPredicate(
      (widget) =>
          widget is TextField && widget.decoration?.labelText == 'Datum',
    );

    final timeField = find.byWidgetPredicate(
      (widget) =>
          widget is TextField && widget.decoration?.labelText == 'Uhrzeit',
    );

    final noteField = find.byWidgetPredicate(
      (widget) =>
          widget is TextField &&
          widget.decoration?.labelText == 'Notiz (optional)',
    );

    await tester.enterText(doctorField, 'Zahnarzt');
    await tester.enterText(noteField, 'Jährliche Kontrolle');

    await tester.tap(dateField);
    await tester.pumpAndSettle();
    await tester.tap(find.text('OK'));
    await tester.pumpAndSettle();

    await tester.tap(timeField);
    await tester.pumpAndSettle();
    await tester.tap(find.text('OK'));
    await tester.pumpAndSettle();

    await tester.tap(find.text('Speichern'));
    await tester.pumpAndSettle();

    expect(controller.appointments.value, hasLength(1));
    expect(controller.appointments.value.first.doctorName, equals('Zahnarzt'));
    expect(
      controller.appointments.value.first.note,
      equals('Jährliche Kontrolle'),
    );
    expect(controller.appointments.value.first.appointmentDate, isNotNull);

    expect(find.text('Termin hinzufügen'), findsNothing);
    expect(find.text('Zahnarzt'), findsOneWidget);
    expect(find.text('Jährliche Kontrolle'), findsOneWidget);
    expect(find.text('Termin gespeichert'), findsOneWidget);
  });

  testWidgets('deletes an existing appointment', (tester) async {
    controller.addAppointment(
      Appointment(
        id: 'delete-test',
        doctorName: 'Augenarzt',
        appointmentDate: DateTime(2026, 8, 20, 10),
        note: 'Sehtest',
      ),
    );

    await pumpAppointmentScreen(tester);

    expect(find.text('Augenarzt'), findsOneWidget);

    await tester.tap(find.byTooltip('Termin löschen'));
    await tester.pumpAndSettle();

    expect(find.text('Termin löschen'), findsOneWidget);
    expect(find.textContaining('Augenarzt'), findsWidgets);

    await tester.tap(find.widgetWithText(FilledButton, 'Löschen'));
    await tester.pumpAndSettle();

    expect(controller.appointments.value, isEmpty);
    expect(find.text('Augenarzt'), findsNothing);
    expect(find.text('Noch keine Termine vorhanden'), findsOneWidget);
    expect(find.text('Termin gelöscht'), findsOneWidget);
  });

  testWidgets('edits an existing appointment', (tester) async {
    controller.addAppointment(
      Appointment(
        id: 'edit-test',
        doctorName: 'Hausarzt',
        appointmentDate: DateTime(2026, 8, 20, 10),
        note: 'Alte Notiz',
      ),
    );

    await pumpAppointmentScreen(tester);

    await tester.tap(find.byTooltip('Termin bearbeiten'));
    await tester.pumpAndSettle();

    expect(find.text('Termin bearbeiten'), findsOneWidget);

    final doctorField = find.byWidgetPredicate(
      (widget) => widget is TextField && widget.decoration?.labelText == 'Arzt',
    );

    final noteField = find.byWidgetPredicate(
      (widget) =>
          widget is TextField &&
          widget.decoration?.labelText == 'Notiz (optional)',
    );

    expect(tester.widget<TextField>(doctorField).controller?.text, 'Hausarzt');
    expect(tester.widget<TextField>(noteField).controller?.text, 'Alte Notiz');

    await tester.enterText(doctorField, 'Hautarzt');
    await tester.enterText(noteField, 'Neue Notiz');

    await tester.tap(find.text('Speichern'));
    await tester.pumpAndSettle();

    expect(controller.appointments.value, hasLength(1));
    expect(controller.appointments.value.first.doctorName, 'Hautarzt');
    expect(controller.appointments.value.first.note, 'Neue Notiz');

    expect(find.text('Hausarzt'), findsNothing);
    expect(find.text('Alte Notiz'), findsNothing);
    expect(find.text('Hautarzt'), findsOneWidget);
    expect(find.text('Neue Notiz'), findsOneWidget);
    expect(find.text('Termin aktualisiert'), findsOneWidget);
  });

  testWidgets('does not overflow on a short web viewport', (tester) async {
    await tester.binding.setSurfaceSize(const Size(1200, 350));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(const MaterialApp(home: AppointmentScreen()));

    await tester.pumpAndSettle();

    expect(find.text('Terminplanung'), findsOneWidget);
    expect(find.text('Deine Termine'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}