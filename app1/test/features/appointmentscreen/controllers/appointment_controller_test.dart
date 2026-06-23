import 'package:flutter_test/flutter_test.dart';
import 'package:app1/features/appointmentscreen/controllers/appointment_controller.dart';
import 'package:app1/features/appointmentscreen/data/models/appointment.dart';

void main() {
  late AppointmentController controller;

  setUp(() {
    controller = AppointmentController();

    controller.appointments.value = [];
  });

  test('adds an appointment', () {
    final appointment = Appointment(
      id: '1',
      doctorName: 'Hausarzt',
      appointmentDate: DateTime(2026, 7, 10, 10),
      note: 'Kontrolltermin',
    );

    controller.addAppointment(appointment);

    expect(controller.appointments.value, hasLength(1));
    expect(controller.appointments.value.first.doctorName, equals('Hausarzt'));
  });

  test('removes an appointment', () {
    final appointment = Appointment(id: '1', doctorName: 'Hausarzt', note: '');

    controller.addAppointment(appointment);
    controller.removeAppointment('1');

    expect(controller.appointments.value, isEmpty);
  });

  test('updates an appointment', () {
    final appointment = Appointment(id: '1', doctorName: 'Hausarzt', note: '');

    final updatedAppointment = Appointment(
      id: '1',
      doctorName: 'Zahnarzt',
      note: 'Kontrolle',
    );

    controller.addAppointment(appointment);
    controller.updateAppointment(updatedAppointment);

    expect(controller.appointments.value, hasLength(1));
    expect(controller.appointments.value.first.doctorName, equals('Zahnarzt'));
    expect(controller.appointments.value.first.note, equals('Kontrolle'));
  });

  test('toggles completed state', () {
    final appointment = Appointment(id: '1', doctorName: 'Hausarzt', note: '');

    controller.addAppointment(appointment);
    controller.toggleAppointment('1');

    expect(controller.appointments.value.first.isCompleted, isTrue);

    controller.toggleAppointment('1');

    expect(controller.appointments.value.first.isCompleted, isFalse);
  });

  test('does not add the same recommendation twice', () {
    final firstRecommendation = Appointment(
      id: '1',
      doctorName: 'Hausarzttermin vereinbaren',
      note: '',
      isRecommendation: true,
    );

    final duplicateRecommendation = Appointment(
      id: '2',
      doctorName: 'Hausarzttermin vereinbaren',
      note: '',
      isRecommendation: true,
    );

    final firstWasAdded = controller.addRecommendedAppointmentIfMissing(
      firstRecommendation,
    );

    final duplicateWasAdded = controller.addRecommendedAppointmentIfMissing(
      duplicateRecommendation,
    );

    expect(firstWasAdded, isTrue);
    expect(duplicateWasAdded, isFalse);
    expect(controller.appointments.value, hasLength(1));
  });
}
