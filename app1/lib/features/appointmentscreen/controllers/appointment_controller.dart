import 'package:flutter/material.dart';

import '../data/models/appointment.dart';

class AppointmentController {
  static final ValueNotifier<List<Appointment>> _sharedAppointments =
      ValueNotifier([]);

  final ValueNotifier<List<Appointment>> appointments = _sharedAppointments;

  void addAppointment(Appointment appointment) {
    appointments.value = [...appointments.value, appointment];
  }

  void removeAppointment(String id) {
    appointments.value = appointments.value
        .where((appointment) => appointment.id != id)
        .toList();
  }

  void dispose() {
    // Shared in-memory appointment state is reused across screens.
  }

  void toggleAppointment(String id) {
    final updatedAppointments = appointments.value.map((appointment) {
      if (appointment.id == id) {
        appointment.isCompleted = !appointment.isCompleted;
      }
      return appointment;
    }).toList();
    appointments.value = updatedAppointments;
  }

  void updateAppointment(Appointment updatedAppointment) {
    appointments.value = appointments.value.map((appointment) {
      if (appointment.id == updatedAppointment.id) {
        return updatedAppointment;
      }

      return appointment;
    }).toList();
  }

  bool addRecommendedAppointmentIfMissing(Appointment appointment) {
    final normalizedDoctorName = appointment.doctorName.trim().toLowerCase();

    final alreadyExists = appointments.value.any((existingAppointment) {
      return existingAppointment.isRecommendation &&
          existingAppointment.profileId == appointment.profileId &&
          (existingAppointment.id == appointment.id ||
              (existingAppointment.doctorName.trim().toLowerCase() ==
                      normalizedDoctorName &&
                  existingAppointment.appointmentDate ==
                      appointment.appointmentDate));
    });

    if (alreadyExists) {
      return false;
    }

    addAppointment(appointment);
    return true;
  }
}
