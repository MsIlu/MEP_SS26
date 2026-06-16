/// Symptom diary entry returned by the backend.
class SymptomResponse {
  final int id;
  final int profileId;
  final DateTime date;
  final String symptom;
  final String bodyArea;
  final int intensity;
  final String note;
  final DateTime createdAt;

  const SymptomResponse({
    required this.id,
    required this.profileId,
    required this.date,
    required this.symptom,
    this.bodyArea = '',
    required this.intensity,
    required this.note,
    required this.createdAt,
  });

  factory SymptomResponse.fromJson(Map<String, dynamic> json) {
    return SymptomResponse(
      id: json['id'] as int,
      profileId: json['profile_id'] as int,
      date: DateTime.parse(json['date'] as String),
      symptom: json['symptom'] as String,
      bodyArea: json['bodyArea'] as String? ?? '',
      intensity: json['intensity'] as int,
      note: json['note'] as String? ?? '',
      createdAt: DateTime.parse(json['createdAt'] as String),
    );
  }
}
