import 'package:app1/core/widgets/shared_day_selector.dart';

/// Returns true when both values point to the same calendar day.
bool isSameMedicationDay(DateTime first, DateTime second) {
  return isSameCalendarDay(first, second);
}

/// Formats the large selected date label above the medication day strip.
String formatMedicationDateTitle(DateTime selectedDate, DateTime today) {
  return formatSharedDateTitle(selectedDate, today);
}

/// Formats compact German weekday labels for the day selector.
String formatMedicationWeekday(DateTime date) {
  return formatSharedWeekday(date);
}

/// Formats compact German month labels for separators in the day strip.
String formatMedicationShortMonth(DateTime date) {
  return formatSharedShortMonth(date);
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