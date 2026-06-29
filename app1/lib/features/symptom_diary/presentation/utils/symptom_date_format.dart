import 'package:app1/core/widgets/shared_day_selector.dart';

/// Returns true when two values point to the same calendar day.
bool isSameSymptomDay(DateTime first, DateTime second) {
  return isSameCalendarDay(first, second);
}

/// Formats the selected diary day for the page header.
String formatSymptomDateTitle(DateTime date, DateTime today) {
  return formatSharedDateTitle(date, today);
}
