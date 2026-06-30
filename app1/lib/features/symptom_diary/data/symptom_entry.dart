import 'dart:convert';

import '../domain/symptom_response.dart';

/// Locally persisted symptom note for one calendar day.
class SymptomEntry {
  int id;
  final DateTime date;
  final String symptom;
  final String bodyArea;
  final int intensity;
  final double? temperatureC;
  final String note;
  final String source;
  final DateTime createdAt;
  final DateTime updatedAt;
  bool isSynced;
  bool pendingUpdate;

  SymptomEntry({
    required this.id,
    required this.date,
    required this.symptom,
    this.bodyArea = '',
    required this.intensity,
    this.temperatureC,
    required this.note,
    this.source = 'manual',
    required this.createdAt,
    DateTime? updatedAt,
    this.isSynced = false,
    this.pendingUpdate = false,
  }) : updatedAt = updatedAt ?? createdAt;

  /// Converts this entry into a SharedPreferences-friendly JSON map.
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'date': date.toIso8601String(),
      'symptom': symptom,
      'bodyArea': bodyArea,
      'intensity': intensity,
      'temperatureC': temperatureC,
      'note': note,
      'source': source,
      'createdAt': createdAt.toIso8601String(),
      'updatedAt': updatedAt.toIso8601String(),
      'isSynced': isSynced,
      'pendingUpdate': pendingUpdate,
    };
  }

  /// Converts a backend response into a locally stored diary entry.
  factory SymptomEntry.fromResponse(SymptomResponse response) {
    return SymptomEntry(
      id: response.id,
      date: DateTime(
        response.date.year,
        response.date.month,
        response.date.day,
      ),
      symptom: response.symptom,
      bodyArea: response.bodyArea,
      intensity: response.intensity,
      temperatureC: response.temperatureC,
      note: response.note,
      source: response.source,
      createdAt: response.createdAt,
      updatedAt: response.updatedAt,
      isSynced: true,
      pendingUpdate: false,
    );
  }

  /// Restores an entry from local JSON.
  factory SymptomEntry.fromJson(Map<String, dynamic> json) {
    return SymptomEntry(
      id: json['id'] as int,
      date: DateTime.parse(json['date'] as String),
      symptom: json['symptom'] as String,
      bodyArea: json['bodyArea'] as String? ?? '',
      intensity: json['intensity'] as int,
      temperatureC: (json['temperatureC'] as num?)?.toDouble(),
      note: json['note'] as String? ?? '',
      source: json['source'] as String? ?? 'manual',
      createdAt: DateTime.parse(json['createdAt'] as String),
      updatedAt: DateTime.tryParse(json['updatedAt'] as String? ?? ''),
      isSynced: json['isSynced'] as bool? ?? false,
      pendingUpdate: json['pendingUpdate'] as bool? ?? false,
    );
  }

  SymptomEntry copyWith({
    int? id,
    DateTime? date,
    String? symptom,
    String? bodyArea,
    int? intensity,
    double? temperatureC,
    bool clearTemperature = false,
    String? note,
    String? source,
    DateTime? createdAt,
    DateTime? updatedAt,
    bool? isSynced,
    bool? pendingUpdate,
  }) {
    return SymptomEntry(
      id: id ?? this.id,
      date: date ?? this.date,
      symptom: symptom ?? this.symptom,
      bodyArea: bodyArea ?? this.bodyArea,
      intensity: intensity ?? this.intensity,
      temperatureC: clearTemperature ? null : temperatureC ?? this.temperatureC,
      note: note ?? this.note,
      source: source ?? this.source,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      isSynced: isSynced ?? this.isSynced,
      pendingUpdate: pendingUpdate ?? this.pendingUpdate,
    );
  }

  /// Encodes one entry as a string because SharedPreferences stores lists.
  String encode() => jsonEncode(toJson());

  /// Decodes one locally stored entry string.
  static SymptomEntry decode(String value) {
    return SymptomEntry.fromJson(jsonDecode(value) as Map<String, dynamic>);
  }
}
