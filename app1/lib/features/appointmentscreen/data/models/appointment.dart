class Appointment {
  final String id;
  final int? profileId;
  final String doctorName;
  final DateTime? appointmentDate;
  final String note;
  final bool isRecommendation;

  bool isCompleted;

  Appointment({
    required this.id,
    this.profileId,
    required this.doctorName,
    this.appointmentDate,
    required this.note,
    this.isRecommendation = false,
    this.isCompleted = false,
  });
}
