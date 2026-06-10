import 'package:flutter/material.dart';

/// Supported intake patterns for user-managed medication schedules.
enum MedicationFrequency {
  daily,
  twiceDaily,
  weekdays,
  weekly,
  monthly;

  /// User-facing German label for form fields and medication cards.
  String get label {
    return switch (this) {
      MedicationFrequency.daily => 'Täglich',
      MedicationFrequency.twiceDaily => '2x täglich',
      MedicationFrequency.weekdays => 'Werktags',
      MedicationFrequency.weekly => 'Wöchentlich',
      MedicationFrequency.monthly => 'Monatlich',
    };
  }

  /// Stable value used in persisted JSON.
  String get storageValue {
    return switch (this) {
      MedicationFrequency.daily => 'daily',
      MedicationFrequency.twiceDaily => 'twice_daily',
      MedicationFrequency.weekdays => 'weekdays',
      MedicationFrequency.weekly => 'weekly',
      MedicationFrequency.monthly => 'monthly',
    };
  }

  /// Restores stored values and defaults old entries to daily schedules.
  static MedicationFrequency fromStorageValue(String? value) {
    return switch (value) {
      'twice_daily' => MedicationFrequency.twiceDaily,
      'weekdays' => MedicationFrequency.weekdays,
      'weekly' => MedicationFrequency.weekly,
      'monthly' => MedicationFrequency.monthly,
      _ => MedicationFrequency.daily,
    };
  }
}

/// Builds the ordered intake times for a schedule.
List<TimeOfDay> medicationIntakeTimes({
  required MedicationFrequency frequency,
  required TimeOfDay firstIntakeTime,
  TimeOfDay? secondIntakeTime,
}) {
  final times = [
    firstIntakeTime,
    if (frequency == MedicationFrequency.twiceDaily)
      secondIntakeTime ?? const TimeOfDay(hour: 20, minute: 0),
  ];

  return times..sort(_compareTimes);
}

/// Orders TimeOfDay values without needing DateTime objects.
int _compareTimes(TimeOfDay first, TimeOfDay second) {
  final firstMinutes = first.hour * 60 + first.minute;
  final secondMinutes = second.hour * 60 + second.minute;

  return firstMinutes.compareTo(secondMinutes);
}