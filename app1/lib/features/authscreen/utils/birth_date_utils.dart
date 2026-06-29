class BirthDateUtils {
  static int earliestAllowedYear({DateTime? now}) {
    return (now ?? DateTime.now()).year - 150;
  }

  static int latestAllowedYear({DateTime? now}) {
    return (now ?? DateTime.now()).year;
  }

  static DateTime? parse(String value) {
    final match = RegExp(r'^(\d{2})\.(\d{2})\.(\d{4})$').firstMatch(value);
    if (match == null) {
      return null;
    }

    final day = int.parse(match.group(1)!);
    final month = int.parse(match.group(2)!);
    final year = int.parse(match.group(3)!);
    final parsed = DateTime(year, month, day);

    if (parsed.day != day || parsed.month != month || parsed.year != year) {
      return null;
    }
    return parsed;
  }

  static int? calculateAge(String value, {DateTime? now}) {
    if (validate(value, now: now) != null) {
      return null;
    }

    final birthDate = parse(value);
    if (birthDate == null) {
      return null;
    }

    final today = now ?? DateTime.now();
    var age = today.year - birthDate.year;
    final birthdayHasPassed =
        today.month > birthDate.month ||
        (today.month == birthDate.month && today.day >= birthDate.day);

    if (!birthdayHasPassed) {
      age -= 1;
    }
    return age;
  }

  static String? validate(String? value, {DateTime? now}) {
    final rawValue = value?.trim() ?? '';
    if (!RegExp(r'^\d{2}\.\d{2}\.\d{4}$').hasMatch(rawValue)) {
      return 'Bitte nutze das Format TT.MM.JJJJ.';
    }

    const invalidMessage = 'Bitte gib ein gültiges Geburtsdatum ein.';
    final birthDate = parse(rawValue);
    if (birthDate == null) {
      return invalidMessage;
    }

    final today = now ?? DateTime.now();
    final currentYear = today.year;
    final earliestYear = currentYear - 150;

    if (birthDate.year > currentYear) {
      return invalidMessage;
    }
    if (birthDate.year < earliestYear) {
      return invalidMessage;
    }
    if (birthDate.isAfter(today)) {
      return invalidMessage;
    }
    return null;
  }
}
