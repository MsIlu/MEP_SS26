class Appointment {
  final String id;
  final String doctorName;
  final DateTime appointmentDate;
  final String note;

  bool isCompleted;

  Appointment({
    required this.id,
    required this.doctorName,
    required this.appointmentDate,
    required this.note,
    this.isCompleted = false,
  });
}