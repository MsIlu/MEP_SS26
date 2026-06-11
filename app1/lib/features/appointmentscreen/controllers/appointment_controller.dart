import 'package:flutter/material.dart';
import '../data/models/appointment.dart';

class AppointmentController {
  final ValueNotifier<List<Appointment>> appointments =
      ValueNotifier([]);

  void addAppointment(Appointment appointment) {
    appointments.value = [
      ...appointments.value,
      appointment,
    ];
  }
  void removeAppointment(String id) {
    appointments.value = appointments.value
        .where((appointment) => appointment.id != id)
        .toList();
  }
  void dispose() {
    appointments.dispose();
  }
  void toggleAppointment(String id) {
  final updatedAppointments =
      appointments.value.map((appointment) {
    if (appointment.id == id) {
      appointment.isCompleted =
          !appointment.isCompleted;
    }
    return appointment;
    }).toList();
  appointments.value = updatedAppointments;
}
void updateAppointment(Appointment updatedAppointment) {
  appointments.value =
      appointments.value.map((appointment) {
    if (appointment.id == updatedAppointment.id) {
      return updatedAppointment;
    }

    return appointment;
  }).toList();
}
}