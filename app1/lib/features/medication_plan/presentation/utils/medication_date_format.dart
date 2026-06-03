const _weekdays = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So'];
const _months = [
  'Januar',
  'Februar',
  'März',
  'April',
  'Mai',
  'Juni',
  'Juli',
  'August',
  'September',
  'Oktober',
  'November',
  'Dezember',
];

const _shortMonths = [
  'Jan',
  'Feb',
  'Mär',
  'Apr',
  'Mai',
  'Jun',
  'Jul',
  'Aug',
  'Sep',
  'Okt',
  'Nov',
  'Dez',
];

/// Returns true when both values point to the same calendar day.
bool isSameMedicationDay(DateTime first, DateTime second) {
  return first.year == second.year &&
      first.month == second.month &&
      first.day == second.day;
}

/// Formats the large selected date label above the medication day strip.
String formatMedicationDateTitle(DateTime selectedDate, DateTime today) {
  final month = _months[selectedDate.month - 1];
  if (isSameMedicationDay(selectedDate, today)) {
    return 'Heute, ${selectedDate.day}. $month';
  }

  return '${formatMedicationWeekday(selectedDate)}., ${selectedDate.day}. $month';
}

/// Formats compact German weekday labels for the day selector.
String formatMedicationWeekday(DateTime date) {
  return _weekdays[date.weekday - 1];
}

/// Formats compact German month labels for separators in the day strip.
String formatMedicationShortMonth(DateTime date) {
  return _shortMonths[date.month - 1];
}

/// Returns a stable date key for per-day medication intake state.
String medicationDateKey(DateTime date) {
  final month = date.month.toString().padLeft(2, '0');
  final day = date.day.toString().padLeft(2, '0');
  return '${date.year}-$month-$day';
}

/// Returns a stable per-dose intake key for one medication on one day.
String medicationDoseDateKey(DateTime date, int doseIndex) {
  final dateKey = medicationDateKey(date);

  return doseIndex == 0 ? dateKey : '$dateKey#$doseIndex';
}