import 'package:app1/core/widgets/shared_day_selector/shared_day_selector_date_utils.dart';
import 'package:app1/core/widgets/shared_day_selector/shared_day_selector_strip.dart';
import 'package:flutter/material.dart';

export 'package:app1/core/widgets/shared_day_selector/shared_day_selector_date_utils.dart';
export 'package:app1/core/widgets/shared_day_selector/shared_day_selector_metrics.dart';

/// Shared horizontal day selector for diary-style feature pages.
class SharedDaySelector extends StatelessWidget {
  final DateTime selectedDate;
  final DateTime today;
  final ValueChanged<DateTime> onDateSelected;
  final bool Function(DateTime date)? hasMarker;
  final bool Function(DateTime date)? isDateEnabled;

  const SharedDaySelector({
    super.key,
    required this.selectedDate,
    required this.today,
    required this.onDateSelected,
    this.hasMarker,
    this.isDateEnabled,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          formatSharedDateTitle(selectedDate, today),
          textAlign: TextAlign.center,
          style: TextStyle(
            color: Theme.of(context).colorScheme.onSurface,
            fontSize: 25,
            fontWeight: FontWeight.w800,
          ),
        ),
        const SizedBox(height: 12),
        SharedDaySelectorStrip(
          selectedDate: selectedDate,
          today: today,
          onDateSelected: onDateSelected,
          hasMarker: hasMarker,
          isDateEnabled: isDateEnabled,
        ),
      ],
    );
  }
}
