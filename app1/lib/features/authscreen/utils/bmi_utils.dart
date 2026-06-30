class BmiUtils {
  static double? calculate({
    required String heightCm,
    required String weightKg,
  }) {
    final height = int.tryParse(heightCm.trim());
    final weight = double.tryParse(weightKg.trim().replaceAll(',', '.'));
    if (height == null || height <= 0 || weight == null || weight <= 0) {
      return null;
    }

    final heightInMeters = height / 100;
    return weight / (heightInMeters * heightInMeters);
  }

  static String format(double bmi) {
    return bmi.toStringAsFixed(1).replaceAll('.', ',');
  }
}
