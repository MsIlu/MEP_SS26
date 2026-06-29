import 'package:flutter/material.dart';

import '../../utils/medication_date_format.dart';
import 'medication_day_selector_metrics.dart';

/// Separator shown when the horizontal date strip crosses into a new month.
class MonthBoundarySeparator extends StatelessWidget {
  final DateTime monthDate;

  const MonthBoundarySeparator({super.key, required this.monthDate});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return SizedBox(
      width: MedicationDaySelectorMetrics.monthSeparatorWidth,
      child: Stack(
        children: [
          Positioned(
            left: 10,
            top: 20,
            bottom: 8,
            child: Container(
              width: 1,
              color: colorScheme.outlineVariant.withValues(alpha: 0.65),
            ),
          ),
          Positioned(
            left: 17,
            top: 0,
            child: Text(
              formatMedicationShortMonth(monthDate),
              style: TextStyle(
                color: colorScheme.onSurfaceVariant,
                fontSize: 11,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
