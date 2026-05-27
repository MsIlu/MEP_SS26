import 'birth_date_utils.dart';

class AuthValidators {
  static String? requiredText(String? value) {
    if ((value ?? '').trim().isEmpty) {
      return 'Bitte ausfüllen.';
    }
    return null;
  }

  static String? nameText(String? value) {
    final requiredError = requiredText(value);
    if (requiredError != null) {
      return requiredError;
    }
    if (RegExp(r'\d').hasMatch(value ?? '')) {
      return 'Bitte keine Zahlen eingeben.';
    }
    return null;
  }

  static String? email(String? value) {
    final email = value?.trim() ?? '';
    if (email.isEmpty) {
      return 'Bitte gib deine E-Mail-Adresse ein.';
    }
    if (!RegExp(r'^[^@\s]+@[^@\s]+\.[^@\s]+$').hasMatch(email)) {
      return 'Bitte gib eine gültige E-Mail-Adresse ein.';
    }
    return null;
  }

  static String? loginPassword(String? value) {
    if ((value ?? '').isEmpty) {
      return 'Bitte gib dein Passwort ein.';
    }
    return null;
  }

  static String? newPassword(String? value) {
    if ((value ?? '').length < 8) {
      return 'Das Passwort braucht mindestens 8 Zeichen.';
    }
    return null;
  }

  static String? passwordConfirmation(String? value, String password) {
    if (value != password) {
      return 'Die Passwörter stimmen nicht überein.';
    }
    return null;
  }

  static String? birthDate(String? value) {
    return BirthDateUtils.validate(value);
  }

  static String? heightCm(String? value) {
    final height = int.tryParse(value?.trim() ?? '');
    if (height == null || height <= 0 || height > 250) {
      return 'Bitte eine Größe zwischen 1 und 250 cm eintragen.';
    }
    return null;
  }

  static String? weightKg(String? value) {
    final normalizedValue = (value ?? '').trim().replaceAll(',', '.');
    final weight = double.tryParse(normalizedValue);
    if (weight == null || weight <= 0) {
      return 'Bitte ein Gewicht größer als 0 kg eintragen.';
    }
    return null;
  }
}
