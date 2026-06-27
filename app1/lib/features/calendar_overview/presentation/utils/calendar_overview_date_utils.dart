/// Returns true when both dates point to the same calendar day.
bool isSameCalendarDay(DateTime first, DateTime second) {
  return first.year == second.year &&
      first.month == second.month &&
      first.day == second.day;
}

/// Builds month cells with blank placeholders before and after the current month.
List<DateTime?> visibleMonthDays(DateTime month) {
  final firstDay = DateTime(month.year, month.month);
  final leadingDays = firstDay.weekday - DateTime.monday;
  final daysInMonth = DateTime(month.year, month.month + 1, 0).day;
  final currentMonthDays = List<DateTime?>.generate(
    daysInMonth,
    (index) => DateTime(month.year, month.month, index + 1),
  );
  final totalCells = leadingDays + currentMonthDays.length;
  final trailingDays = (7 - totalCells % 7) % 7;

  return [
    ...List<DateTime?>.filled(leadingDays, null),
    ...currentMonthDays,
    ...List<DateTime?>.filled(trailingDays, null),
  ];
}

String calendarMonthLabel(DateTime date) {
  return '${calendarMonthName(date.month)} ${date.year}';
}

String calendarDateLabel(DateTime date) {
  return '${date.day}. ${calendarMonthName(date.month)} ${date.year}';
}

String calendarMonthName(int month) {
  return const [
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
  ][month - 1];
}

String twoDigits(int value) => value.toString().padLeft(2, '0');
