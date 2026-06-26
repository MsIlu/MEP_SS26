import 'package:app1/core/themes/app_colors.dart';
import 'package:app1/features/calendar_overview/presentation/utils/calendar_overview_date_utils.dart';
import 'package:flutter/material.dart';

/// Compact month grid that only renders days from the focused month.
class CalendarMonthGrid extends StatelessWidget {
  final DateTime focusedMonth;
  final DateTime selectedDate;
  final DateTime today;
  final bool Function(DateTime date) hasItems;
  final ValueChanged<DateTime> onSelected;

  const CalendarMonthGrid({
    super.key,
    required this.focusedMonth,
    required this.selectedDate,
    required this.today,
    required this.hasItems,
    required this.onSelected,
  });

  @override
  Widget build(BuildContext context) {
    final days = visibleMonthDays(focusedMonth);

    return Column(
      children: [
        Row(
          children: [
            for (final label in ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So'])
              Expanded(child: Center(child: Text(label))),
          ],
        ),
        const SizedBox(height: 8),
        GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: days.length,
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 7,
            childAspectRatio: 1.35,
            mainAxisSpacing: 4,
            crossAxisSpacing: 4,
          ),
          itemBuilder: (context, index) {
            final date = days[index];
            if (date == null) return const SizedBox.shrink();

            return _CalendarDayTile(
              date: date,
              isSelected: isSameCalendarDay(date, selectedDate),
              isToday: isSameCalendarDay(date, today),
              hasMarker: hasItems(date),
              onTap: () => onSelected(date),
            );
          },
        ),
      ],
    );
  }
}

class _CalendarDayTile extends StatelessWidget {
  final DateTime date;
  final bool isSelected;
  final bool isToday;
  final bool hasMarker;
  final VoidCallback onTap;

  const _CalendarDayTile({
    required this.date,
    required this.isSelected,
    required this.isToday,
    required this.hasMarker,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    final accentColor = isDarkMode
        ? AppColors.careenaAccentOnDark
        : AppColors.careenaTeal;
    final backgroundColor = isSelected
        ? AppColors.careenaTeal
        : isDarkMode
        ? AppColors.darkElevatedSurface
        : AppColors.careenaNoteBackground;
    final textColor = isSelected ? AppColors.white : colorScheme.onSurface;

    return InkWell(
      borderRadius: BorderRadius.circular(8),
      onTap: onTap,
      child: DecoratedBox(
        decoration: BoxDecoration(
          color: backgroundColor,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: isSelected || isToday
                ? accentColor
                : AppColors.careenaBorder,
            width: isToday && !isSelected ? 2 : 1,
          ),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              '${date.day}',
              style: TextStyle(color: textColor, fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 4),
            SizedBox.square(
              dimension: 5,
              child: DecoratedBox(
                decoration: BoxDecoration(
                  color: hasMarker
                      ? (isSelected ? AppColors.white : accentColor)
                      : AppColors.transparent,
                  shape: BoxShape.circle,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
