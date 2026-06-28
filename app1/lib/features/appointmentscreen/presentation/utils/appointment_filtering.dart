import '../../data/models/appointment.dart';

/// Separates appointments into the sections shown by the appointment list.
AppointmentSections buildAppointmentSections(
  List<Appointment> appointments,
  String selectedFilter, {
  DateTime? now,
}) {
  final filtered = _filterAppointments(
    appointments,
    selectedFilter,
    now ?? DateTime.now(),
  );
  final recommendedAppointments = selectedFilter == 'Alle'
      ? filtered.where(_isPendingRecommendation).toList()
      : <Appointment>[];
  final plannedAppointments = filtered
      .where((appointment) => !_isPendingRecommendation(appointment))
      .toList()
    ..sort(_compareAppointmentDates);

  return AppointmentSections(
    recommendedAppointments: recommendedAppointments,
    plannedAppointments: plannedAppointments,
  );
}

List<Appointment> _filterAppointments(
  List<Appointment> appointments,
  String selectedFilter,
  DateTime now,
) {
  return switch (selectedFilter) {
    'Kommend' => appointments.where((appointment) {
        final date = appointment.appointmentDate;
        return date != null && date.isAfter(now);
      }).toList(),
    'Vergangen' => appointments.where((appointment) {
        final date = appointment.appointmentDate;
        return date != null && date.isBefore(now);
      }).toList(),
    'Erledigt' => appointments
        .where((appointment) => appointment.isCompleted)
        .toList(),
    _ => List<Appointment>.from(appointments),
  };
}

bool _isPendingRecommendation(Appointment appointment) {
  return appointment.isRecommendation && appointment.appointmentDate == null;
}

int _compareAppointmentDates(Appointment first, Appointment second) {
  final firstDate = first.appointmentDate;
  final secondDate = second.appointmentDate;

  if (firstDate == null && secondDate == null) return 0;
  if (firstDate == null) return -1;
  if (secondDate == null) return 1;

  return firstDate.compareTo(secondDate);
}

class AppointmentSections {
  final List<Appointment> recommendedAppointments;
  final List<Appointment> plannedAppointments;

  const AppointmentSections({
    required this.recommendedAppointments,
    required this.plannedAppointments,
  });

  bool get isEmpty => recommendedAppointments.isEmpty && plannedAppointments.isEmpty;
}
