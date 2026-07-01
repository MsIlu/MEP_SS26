import 'package:flutter/material.dart';

import '../data/models/appointment.dart';

class AppointmentController {
  static final ValueNotifier<List<Appointment>> _sharedAppointments =
      ValueNotifier([]);

  final ValueNotifier<List<Appointment>> appointments = _sharedAppointments;

  void addAppointment(Appointment appointment) {
    appointments.value = _deduplicateRecommendedAppointments([
      ...appointments.value,
      appointment,
    ]);
  }

  void removeAppointment(String id) {
    appointments.value = appointments.value
        .where((appointment) => appointment.id != id)
        .toList();
  }

  void clear() {
    appointments.value = [];
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
    if (!appointment.isRecommendation) {
      addAppointment(appointment);
      return true;
    }

    var alreadyExists = false;
    appointments.value = _deduplicateRecommendedAppointments(
      appointments.value.map((existingAppointment) {
        if (_isSameRecommendedAppointment(existingAppointment, appointment)) {
          alreadyExists = true;
          return appointment;
        }

        return existingAppointment;
      }).toList(),
    );

    if (alreadyExists) {
      return false;
    }

    addAppointment(appointment);
    return true;
  }

  void upsertRecommendedAppointments(
    List<Appointment> remoteAppointments, {
    int? profileId,
  }) {
    final preservedAppointments = appointments.value.where((appointment) {
      if (!appointment.isRecommendation) {
        return true;
      }

      if (profileId != null &&
          appointment.profileId == profileId &&
          appointment.backendId != null) {
        return false;
      }

      return !remoteAppointments.any(
        (remoteAppointment) =>
            _isSameRecommendedAppointment(appointment, remoteAppointment),
      );
    }).toList();

    appointments.value = _deduplicateRecommendedAppointments([
      ...preservedAppointments,
      ...remoteAppointments,
    ]);
  }

  List<Appointment> _deduplicateRecommendedAppointments(
    List<Appointment> source,
  ) {
    final result = <Appointment>[];

    for (final appointment in source) {
      if (!appointment.isRecommendation) {
        result.add(appointment);
        continue;
      }

      final existingIndex = result.indexWhere(
        (existingAppointment) =>
            _isSameRecommendedAppointment(existingAppointment, appointment),
      );

      if (existingIndex == -1) {
        result.add(appointment);
      } else {
        result[existingIndex] = appointment;
      }
    }

    return result;
  }

  bool _isSameRecommendedAppointment(Appointment first, Appointment second) {
    if (!first.isRecommendation || !second.isRecommendation) {
      return false;
    }

    if (first.profileId != second.profileId) {
      return false;
    }

    if (first.backendId != null &&
        second.backendId != null &&
        first.backendId == second.backendId) {
      return true;
    }

    if (first.id.trim().isNotEmpty && first.id == second.id) {
      return true;
    }

    return first.doctorName.trim().toLowerCase() ==
            second.doctorName.trim().toLowerCase() &&
        first.appointmentDate == second.appointmentDate;
  }
}
