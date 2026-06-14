class Appointment {
  final String id;
  final String doctorName;
  final DateTime? appointmentDate;
  final String note;
  final bool isRecommendation;

  bool isCompleted;

  Appointment({
    required this.id,
    required this.doctorName,
    this.appointmentDate,
    required this.note,
    this.isRecommendation = false,
    this.isCompleted = false,
  });
}
