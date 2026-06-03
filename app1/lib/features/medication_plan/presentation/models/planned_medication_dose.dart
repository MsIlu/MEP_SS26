import 'package:flutter/material.dart';

import '../../data/medication_entry.dart';

/// One visible medication dose planned for a specific day.
class PlannedMedicationDose {
  final MedicationEntry entry;
  final int doseIndex;
  final TimeOfDay intakeTime;

  const PlannedMedicationDose({
    required this.entry,
    required this.doseIndex,
    required this.intakeTime,
  });
}