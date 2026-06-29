import 'package:flutter/material.dart';

/// Formats medication intake times with a fixed 24-hour clock.
String formatMedicationTime(TimeOfDay time) {
  final hour = time.hour.toString().padLeft(2, '0');
  final minute = time.minute.toString().padLeft(2, '0');
  return '$hour:$minute Uhr';
}

/// Formats multiple intake times for compact schedule descriptions.
String formatMedicationTimes(List<TimeOfDay> times) {
  return times.map(formatMedicationTime).join(', ');
}
