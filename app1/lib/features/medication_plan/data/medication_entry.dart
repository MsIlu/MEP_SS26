import 'dart:convert';

import 'package:flutter/material.dart';

import 'medication_catalog_item.dart';
import 'medication_schedule.dart';

/// Locally persisted medication with dose, schedule, reminder, and intake state.
class MedicationEntry {
  final int id;
  final String name;
  final String dose;
  final TimeOfDay intakeTime;
  final TimeOfDay? secondIntakeTime;
  final MedicationFrequency frequency;
  final bool remindersEnabled;
  final DateTime createdAt;
  final List<String> takenDateKeys;
  final MedicationCatalogItem? catalogItem;

  const MedicationEntry({
    required this.id,
    required this.name,
    required this.dose,
    required this.intakeTime,
    this.secondIntakeTime,
    this.frequency = MedicationFrequency.daily,
    required this.remindersEnabled,
    required this.createdAt,
    this.takenDateKeys = const [],
    this.catalogItem,
  });

  /// Creates an updated entry while preserving unchanged fields.
  MedicationEntry copyWith({
    int? id,
    String? name,
    String? dose,
    TimeOfDay? intakeTime,
    TimeOfDay? secondIntakeTime,
    MedicationFrequency? frequency,
    bool? remindersEnabled,
    DateTime? createdAt,
    List<String>? takenDateKeys,
    MedicationCatalogItem? catalogItem,
  }) {
    return MedicationEntry(
      id: id ?? this.id,
      name: name ?? this.name,
      dose: dose ?? this.dose,
      intakeTime: intakeTime ?? this.intakeTime,
      secondIntakeTime: secondIntakeTime ?? this.secondIntakeTime,
      frequency: frequency ?? this.frequency,
      remindersEnabled: remindersEnabled ?? this.remindersEnabled,
      createdAt: createdAt ?? this.createdAt,
      takenDateKeys: takenDateKeys ?? this.takenDateKeys,
      catalogItem: catalogItem ?? this.catalogItem,
    );
  }

  /// Converts the entry into a SharedPreferences-friendly JSON map.
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'dose': dose,
      'hour': intakeTime.hour,
      'minute': intakeTime.minute,
      'secondHour': secondIntakeTime?.hour,
      'secondMinute': secondIntakeTime?.minute,
      'frequency': frequency.storageValue,
      'remindersEnabled': remindersEnabled,
      'createdAt': createdAt.toIso8601String(),
      'takenDateKeys': takenDateKeys,
      if (catalogItem != null) 'catalogItem': catalogItem!.toJson(),
    };
  }

  /// Restores an entry and keeps older stored data compatible with new fields.
  factory MedicationEntry.fromJson(Map<String, dynamic> json) {
    final now = DateTime.now();

    return MedicationEntry(
      id: json['id'] as int,
      name: json['name'] as String,
      dose: json['dose'] as String,
      intakeTime: TimeOfDay(
        hour: json['hour'] as int,
        minute: json['minute'] as int,
      ),
      secondIntakeTime: json['secondHour'] == null
          ? null
          : TimeOfDay(
              hour: json['secondHour'] as int,
              minute: json['secondMinute'] as int,
            ),
      frequency: MedicationFrequency.fromStorageValue(
        json['frequency'] as String?,
      ),
      remindersEnabled: json['remindersEnabled'] as bool? ?? true,
      createdAt: json['createdAt'] == null
          ? DateTime(now.year, now.month, now.day)
          : DateTime.parse(json['createdAt'] as String),
      takenDateKeys:
          (json['takenDateKeys'] as List<dynamic>?)
              ?.map((value) => value as String)
              .toList() ??
          const [],
      catalogItem: json['catalogItem'] == null
          ? null
          : MedicationCatalogItem.fromJson(
              json['catalogItem'] as Map<String, dynamic>,
            ),
    );
  }

  /// Encodes one entry as a string because SharedPreferences stores string lists.
  String encode() => jsonEncode(toJson());

  /// Returns the intake times that are relevant for this medication schedule.
  List<TimeOfDay> get intakeTimes {
    return medicationIntakeTimes(
      frequency: frequency,
      firstIntakeTime: intakeTime,
      secondIntakeTime: secondIntakeTime,
    );
  }

  /// Returns whether the medication is planned on the given calendar day.
  bool isPlannedOn(DateTime date) {
    final startDay = DateTime(createdAt.year, createdAt.month, createdAt.day);
    final selectedDay = DateTime(date.year, date.month, date.day);

    if (selectedDay.isBefore(startDay)) {
      return false;
    }

    return switch (frequency) {
      MedicationFrequency.daily || MedicationFrequency.twiceDaily => true,
      MedicationFrequency.weekdays => selectedDay.weekday <= DateTime.friday,
      MedicationFrequency.weekly => selectedDay.weekday == startDay.weekday,
      MedicationFrequency.monthly => selectedDay.day == startDay.day,
    };
  }

  /// Decodes one locally stored entry.
  static MedicationEntry decode(String value) {
    return MedicationEntry.fromJson(jsonDecode(value) as Map<String, dynamic>);
  }
}