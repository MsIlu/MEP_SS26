import 'package:flutter/material.dart';

import '../models/auth_review_item.dart';
import '../../utils/birth_date_utils.dart';
import '../../utils/bmi_utils.dart';

class RegistrationFormController {
  // TODO(backend): Replace raw controller reads with a typed registration DTO
  // TODO: once the API contract for account and health-profile creation is defined.
  final personalFormKey = GlobalKey<FormState>();
  final healthFormKey = GlobalKey<FormState>();
  final firstNameController = TextEditingController();
  final lastNameController = TextEditingController();
  final birthDateController = TextEditingController();
  final emailController = TextEditingController();
  final passwordController = TextEditingController();
  final confirmPasswordController = TextEditingController();
  final heightController = TextEditingController();
  final weightController = TextEditingController();
  final notesController = TextEditingController();

  final conditions = <String>{};
  String sex = 'Weiblich';
  bool obscurePassword = true;
  bool obscureConfirmPassword = true;
  bool hasAcceptedConsent = false;

  bool get isPersonalStepValid {
    return personalFormKey.currentState?.validate() ?? false;
  }

  bool get isHealthStepValid {
    return healthFormKey.currentState?.validate() ?? false;
  }

  List<AuthReviewItem> get personalReviewItems {
    final fullName =
        '${firstNameController.text.trim()} ${lastNameController.text.trim()}';
    final age = BirthDateUtils.calculateAge(birthDateController.text);

    return [
      AuthReviewItem(label: 'Name', value: fullName),
      AuthReviewItem(
        label: 'E-Mail-Adresse',
        value: emailController.text.trim(),
      ),
      AuthReviewItem(
        label: 'Geburtsdatum',
        value: birthDateController.text.trim(),
      ),
      AuthReviewItem(
        label: 'Alter',
        value: age == null ? 'Nicht berechnet' : '$age Jahre',
      ),
    ];
  }

  List<AuthReviewItem> get healthReviewItems {
    final bmi = BmiUtils.calculate(
      heightCm: heightController.text,
      weightKg: weightController.text,
    );

    return [
      AuthReviewItem(label: 'Geburtsgeschlecht', value: sex),
      AuthReviewItem(
        label: 'Größe',
        value: '${heightController.text.trim()} cm',
      ),
      AuthReviewItem(
        label: 'Gewicht',
        value: '${weightController.text.trim()} kg',
      ),
      AuthReviewItem(
        label: 'BMI',
        value: bmi == null ? 'Nicht berechnet' : BmiUtils.format(bmi),
      ),
      AuthReviewItem(
        label: 'Vorerkrankungen',
        value: conditions.isEmpty ? 'Keine Angaben' : conditions.join(', '),
      ),
      AuthReviewItem(
        label: 'Weitere Informationen',
        value: notesController.text.trim().isEmpty
            ? 'Keine Angaben'
            : notesController.text.trim(),
      ),
    ];
  }

  void togglePasswordVisibility() {
    obscurePassword = !obscurePassword;
  }

  void toggleConfirmPasswordVisibility() {
    obscureConfirmPassword = !obscureConfirmPassword;
  }

  void updateCondition(String condition, bool selected) {
    if (selected) {
      conditions.add(condition);
    } else {
      conditions.remove(condition);
    }
  }

  void updateConsent(bool accepted) {
    hasAcceptedConsent = accepted;
  }

  void dispose() {
    firstNameController.dispose();
    lastNameController.dispose();
    birthDateController.dispose();
    emailController.dispose();
    passwordController.dispose();
    confirmPasswordController.dispose();
    heightController.dispose();
    weightController.dispose();
    notesController.dispose();
  }
}