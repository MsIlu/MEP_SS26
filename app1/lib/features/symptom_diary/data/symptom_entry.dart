import 'dart:convert';

/// Locally persisted symptom note for one calendar day.
class SymptomEntry {
  final int id;
  final DateTime date;
  final String symptom;
  final String bodyArea;
  final int intensity;
  final String note;
  final DateTime createdAt;

  const SymptomEntry({
    required this.id,
    required this.date,
    required this.symptom,
    this.bodyArea = '',
    required this.intensity,
    required this.note,
    required this.createdAt,
  });

  /// Converts this entry into a SharedPreferences-friendly JSON map.
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'date': date.toIso8601String(),
      'symptom': symptom,
      'bodyArea': bodyArea,
      'intensity': intensity,
      'note': note,
      'createdAt': createdAt.toIso8601String(),
    };
  }

  /// Restores an entry from local JSON.
  factory SymptomEntry.fromJson(Map<String, dynamic> json) {
    return SymptomEntry(
      id: json['id'] as int,
      date: DateTime.parse(json['date'] as String),
      symptom: json['symptom'] as String,
      bodyArea: json['bodyArea'] as String? ?? '',
      intensity: json['intensity'] as int,
      note: json['note'] as String? ?? '',
      createdAt: DateTime.parse(json['createdAt'] as String),
    );
  }

  /// Encodes one entry as a string because SharedPreferences stores lists.
  String encode() => jsonEncode(toJson());

  /// Decodes one locally stored entry string.
  static SymptomEntry decode(String value) {
    return SymptomEntry.fromJson(jsonDecode(value) as Map<String, dynamic>);
  }
}