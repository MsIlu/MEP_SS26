import 'package:app1/core/themes/app_colors.dart';
import 'package:flutter/material.dart';

/// Maps symptom intensity values to simple labels and stable status colors.
class SymptomIntensity {
  SymptomIntensity._();

  static String label(num value) {
    if (value <= 0) {
      return 'Noch keine Daten';
    }
    if (value <= 3) {
      return 'leicht';
    }
    if (value <= 6) {
      return 'mittel';
    }
    return 'stark';
  }

  static Color color(num value) {
    if (value <= 0) {
      return AppColors.symptomIntensityNone;
    }
    if (value <= 3) {
      return AppColors.symptomIntensityLow;
    }
    if (value <= 6) {
      return AppColors.symptomIntensityMedium;
    }
    return AppColors.symptomIntensityHigh;
  }
}
