import 'package:app1/core/themes/app_colors.dart';
import 'package:flutter/material.dart';

import '../../utils/medication_date_format.dart';
import 'medication_day_selector_metrics.dart';

/// One day cell in the medication calendar strip.
class MedicationDayChip extends StatelessWidget {
  final DateTime date;
  final bool isSelected;
  final bool isToday;
  final bool hasPlannedMedication;
  final VoidCallback onTap;

  const MedicationDayChip({
    super.key,
    required this.date,
    required this.isSelected,
    required this.isToday,
    required this.hasPlannedMedication,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    final chipColor = isSelected
        ? AppColors.careenaTeal
        : isDarkMode
        ? AppColors.darkElevatedSurface
        : AppColors.lightBackground;
    final accentColor = isDarkMode
        ? AppColors.careenaAccentOnDark
        : AppColors.careenaTeal;
    final unselectedDayColor = isDarkMode
        ? colorScheme.onSurfaceVariant
        : AppColors.careenaDark;
    final dayColor = isSelected || isToday
        ? accentColor
        : unselectedDayColor;
    final dateColor = isSelected ? AppColors.white : colorScheme.onSurface;

    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(18),
      child: SizedBox(
        width: MedicationDaySelectorMetrics.chipWidth,
        child: Column(
          mainAxisAlignment: MainAxisAlignment.end,
          children: [
            AnimatedOpacity(
              duration: const Duration(milliseconds: 160),
              opacity: isSelected ? 1 : 0,
              child: Icon(
                Icons.arrow_drop_down,
                color: accentColor,
                size: 18,
              ),
            ),
            Text(
              formatMedicationWeekday(date),
              style: TextStyle(color: dayColor, fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 4),
            AnimatedContainer(
              duration: const Duration(milliseconds: 160),
              width: 42,
              height: 42,
              alignment: Alignment.center,
              decoration: BoxDecoration(
                color: chipColor,
                shape: BoxShape.circle,
                border: Border.all(
                  color: isToday && !isSelected
                      ? accentColor
                      : AppColors.transparent,
                  width: 1.5,
                ),
              ),
              child: Text(
                '${date.day}',
                style: TextStyle(color: dateColor, fontWeight: FontWeight.w800),
              ),
            ),
            const SizedBox(height: 4),
            AnimatedContainer(
              duration: const Duration(milliseconds: 160),
              width: hasPlannedMedication ? 6 : 0,
              height: 6,
              decoration: BoxDecoration(
                color: hasPlannedMedication
                    ? accentColor
                    : AppColors.transparent,
                shape: BoxShape.circle,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
