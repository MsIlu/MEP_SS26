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

  test('clears all appointments on logout', () {
    controller.addAppointment(
      Appointment(id: '1', profileId: 10, doctorName: 'Hausarzt', note: ''),
    );

    controller.clear();

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

  test('does not add the same dated FHIR recommendation twice', () {
    final appointmentDate = DateTime(2026, 7, 2, 9, 30);
    final firstRecommendation = Appointment(
      id: 'hapi-appointment-1',
      doctorName: 'Hausarztpraxis Dr. Schneider',
      appointmentDate: appointmentDate,
      note: '',
      isRecommendation: true,
    );

    final duplicateRecommendation = Appointment(
      id: 'hapi-appointment-1',
      doctorName: 'Hausarztpraxis Dr. Schneider',
      appointmentDate: appointmentDate,
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

  test(
    'upserts remote recommended appointments without removing manual ones',
    () {
      final manualAppointment = Appointment(
        id: 'manual-1',
        doctorName: 'Zahnarzt',
        appointmentDate: DateTime(2026, 7, 1, 11),
        note: 'Kontrolle',
      );
      final staleRecommendation = Appointment(
        id: 'hapi-appointment-1',
        profileId: 10,
        doctorName: 'Alter Praxisname',
        appointmentDate: DateTime(2026, 7, 2, 9, 30),
        note: '',
        isRecommendation: true,
      );
      final remoteRecommendation = Appointment(
        id: 'hapi-appointment-1',
        profileId: 10,
        doctorName: 'Hausarztpraxis Dr. Schneider',
        appointmentDate: DateTime(2026, 7, 2, 9, 30),
        note: 'Von Careena empfohlen',
        isRecommendation: true,
      );

      controller.addAppointment(manualAppointment);
      controller.addAppointment(staleRecommendation);

      controller.upsertRecommendedAppointments([remoteRecommendation]);

      expect(controller.appointments.value, hasLength(2));
      expect(
        controller.appointments.value.where(
          (appointment) => appointment.id == 'manual-1',
        ),
        hasLength(1),
      );
      expect(
        controller.appointments.value
            .where((appointment) => appointment.id == 'hapi-appointment-1')
            .single
            .doctorName,
        'Hausarztpraxis Dr. Schneider',
      );
    },
  );

  test('removes stale remote appointments when the server returns none', () {
    controller.addAppointment(
      Appointment(
        id: 'remote-1',
        backendId: 1,
        profileId: 10,
        doctorName: 'Hausarzt',
        note: '',
        isRecommendation: true,
      ),
    );

    controller.upsertRecommendedAppointments([], profileId: 10);

    expect(controller.appointments.value, isEmpty);
  });
}
