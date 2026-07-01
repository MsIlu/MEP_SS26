class Appointment {
  final String id;
  final int? backendId;
  final int? profileId;
  final String? sessionId;
  final String doctorName;
  final DateTime? appointmentDate;
  final String note;
  final bool isRecommendation;

  bool isCompleted;

  Appointment({
    required this.id,
    this.backendId,
    this.profileId,
    this.sessionId,
    required this.doctorName,
    this.appointmentDate,
    required this.note,
    this.isRecommendation = false,
    this.isCompleted = false,
  });
}
