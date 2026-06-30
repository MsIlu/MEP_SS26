import 'package:app1/core/widgets/shared_day_selector/shared_day_selector_metrics.dart';

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

bool isSameCalendarDay(DateTime first, DateTime second) {
  return first.year == second.year &&
      first.month == second.month &&
      first.day == second.day;
}

String formatSharedDateTitle(DateTime selectedDate, DateTime today) {
  final month = _months[selectedDate.month - 1];
  if (isSameCalendarDay(selectedDate, today)) {
    return 'Heute, ${selectedDate.day}. $month';
  }

  return '${_weekdays[selectedDate.weekday - 1]}, ${selectedDate.day}. $month';
}

String formatSharedWeekday(DateTime date) => _weekdays[date.weekday - 1];

String formatSharedFullDate(DateTime date, DateTime today) {
  final month = _months[date.month - 1];
  if (isSameCalendarDay(date, today)) {
    return 'Heute, ${date.day}. $month ${date.year}';
  }

  return '${_weekdays[date.weekday - 1]}, ${date.day}. $month ${date.year}';
}

String formatSharedShortMonth(DateTime date) => _shortMonths[date.month - 1];

List<DateTime> buildSharedDayRange(DateTime today) {
  return List.generate(
    SharedDaySelectorMetrics.dayCount,
    (index) => DateTime(
      today.year,
      today.month,
      today.day + index - SharedDaySelectorMetrics.todayIndex,
    ),
  );
}
