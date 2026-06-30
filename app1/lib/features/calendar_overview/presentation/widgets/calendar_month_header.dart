import 'package:app1/features/calendar_overview/presentation/utils/calendar_overview_date_utils.dart';
import 'package:flutter/material.dart';

/// Month switcher for the compact calendar overview.
class CalendarMonthHeader extends StatelessWidget {
  final DateTime month;
  final VoidCallback onPrevious;
  final VoidCallback onNext;

  const CalendarMonthHeader({
    super.key,
    required this.month,
    required this.onPrevious,
    required this.onNext,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Semantics(
          button: true,
          label: 'Vorherigen Monat anzeigen',
          onTap: onPrevious,
          child: ExcludeSemantics(
            child: IconButton(
              tooltip: 'Vorherigen Monat anzeigen',
              onPressed: onPrevious,
              icon: const Icon(Icons.chevron_left),
            ),
          ),
        ),
        Expanded(
          child: Text(
            calendarMonthLabel(month),
            textAlign: TextAlign.center,
            style: Theme.of(
              context,
            ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800),
          ),
        ),
        Semantics(
          button: true,
          label: 'Nächsten Monat anzeigen',
          onTap: onNext,
          child: ExcludeSemantics(
            child: IconButton(
              tooltip: 'Nächsten Monat anzeigen',
              onPressed: onNext,
              icon: const Icon(Icons.chevron_right),
            ),
          ),
        ),
      ],
    );
  }
}
