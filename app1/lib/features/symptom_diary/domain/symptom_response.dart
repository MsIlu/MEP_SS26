/// Symptom diary entry returned by the backend.
class SymptomResponse {
  final int id;
  final int profileId;
  final DateTime date;
  final String symptom;
  final String bodyArea;
  final int intensity;
  final double? temperatureC;
  final String note;
  final String source;
  final DateTime createdAt;
  final DateTime updatedAt;

  const SymptomResponse({
    required this.id,
    required this.profileId,
    required this.date,
    required this.symptom,
    this.bodyArea = '',
    required this.intensity,
    this.temperatureC,
    required this.note,
    required this.source,
    required this.createdAt,
    required this.updatedAt,
  });

  factory SymptomResponse.fromJson(Map<String, dynamic> json) {
    return SymptomResponse(
      id: json['id'] as int,
      profileId: json['profile_id'] as int,
      date: DateTime.parse(json['date'] as String),
      symptom: json['symptom'] as String,
      bodyArea: json['bodyArea'] as String? ?? '',
      intensity: json['intensity'] as int,
      temperatureC: (json['temperatureC'] as num?)?.toDouble(),
      note: json['note'] as String? ?? '',
      source: json['source'] as String? ?? 'manual',
      createdAt: DateTime.parse(json['createdAt'] as String),
      updatedAt: DateTime.parse(
        json['updatedAt'] as String? ?? json['createdAt'] as String,
      ),
    );
  }
}
