import 'package:flutter/material.dart';

import '../../../data/medication_entry.dart';
import '../../utils/medication_date_format.dart';
import '../../utils/medication_plan_builder.dart';
import 'day_strip_arrow.dart';
import 'medication_day_chip.dart';
import 'medication_day_selector_metrics.dart';
import 'month_boundary_separator.dart';

/// Horizontal day selector inspired by medication logs, adapted to Careena UI.
class MedicationDaySelector extends StatefulWidget {
  final DateTime selectedDate;
  final DateTime today;
  final List<MedicationEntry> entries;
  final ValueChanged<DateTime> onDateSelected;

  const MedicationDaySelector({
    super.key,
    required this.selectedDate,
    required this.today,
    required this.entries,
    required this.onDateSelected,
  });

  @override
  State<MedicationDaySelector> createState() => _MedicationDaySelectorState();
}

class _MedicationDaySelectorState extends State<MedicationDaySelector> {
  late final ScrollController _scrollController;
  late final List<DateTime> _dates;

  @override
  void initState() {
    super.initState();
    _dates = List.generate(
      MedicationDaySelectorMetrics.dayCount,
      (index) => DateTime(
        widget.today.year,
        widget.today.month,
        widget.today.day + index - MedicationDaySelectorMetrics.todayIndex,
      ),
    );
    _scrollController = ScrollController(
      initialScrollOffset: _offsetForIndex(
        MedicationDaySelectorMetrics.todayIndex,
      ),
    );
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          formatMedicationDateTitle(widget.selectedDate, widget.today),
          textAlign: TextAlign.center,
          style: TextStyle(
            color: Theme.of(context).colorScheme.onSurface,
            fontSize: 25,
            fontWeight: FontWeight.w800,
          ),
        ),
        const SizedBox(height: 12),
        SizedBox(
          height: 102,
          child: Row(
            children: [
              DayStripArrow(
                tooltip: 'Frühere Tage',
                icon: Icons.chevron_left,
                onPressed: () => _scrollByDirection(-1),
              ),
              Expanded(
                child: ShaderMask(
                  shaderCallback: (bounds) {
                    return const LinearGradient(
                      begin: Alignment.centerLeft,
                      end: Alignment.centerRight,
                      colors: [
                        Colors.transparent,
                        Colors.black,
                        Colors.black,
                        Colors.transparent,
                      ],
                      stops: [0, 0.08, 0.92, 1],
                    ).createShader(bounds);
                  },
                  blendMode: BlendMode.dstIn,
                  child: ListView.separated(
                    controller: _scrollController,
                    scrollDirection: Axis.horizontal,
                    padding: const EdgeInsets.symmetric(horizontal: 2),
                    itemCount: _dates.length,
                    separatorBuilder: _buildSeparator,
                    itemBuilder: (context, index) {
                      final date = _dates[index];
                      return MedicationDayChip(
                        date: date,
                        isSelected: isSameMedicationDay(
                          date,
                          widget.selectedDate,
                        ),
                        isToday: isSameMedicationDay(date, widget.today),
                        hasPlannedMedication: hasMedicationPlanForDate(
                          widget.entries,
                          date,
                        ),
                        onTap: () {
                          widget.onDateSelected(date);
                          _scrollToIndex(index);
                        },
                      );
                    },
                  ),
                ),
              ),
              DayStripArrow(
                tooltip: 'Spätere Tage',
                icon: Icons.chevron_right,
                onPressed: () => _scrollByDirection(1),
              ),
            ],
          ),
        ),
      ],
    );
  }

  /// Adds compact gaps inside a week and a labelled divider at month changes.
  Widget _buildSeparator(BuildContext context, int index) {
    final currentDate = _dates[index];
    final nextDate = _dates[index + 1];

    if (currentDate.month != nextDate.month) {
      return MonthBoundarySeparator(monthDate: nextDate);
    }

    if (currentDate.weekday == DateTime.sunday) {
      return const SizedBox(width: MedicationDaySelectorMetrics.weekGap);
    }

    return const SizedBox(width: MedicationDaySelectorMetrics.dayGap);
  }

  /// Calculates a scroll offset that keeps the selected day near the center.
  double _offsetForIndex(int index) {
    var offset = 0.0;
    for (var i = 0; i < index; i++) {
      offset +=
          MedicationDaySelectorMetrics.chipWidth + _separatorWidthAfter(i);
    }

    return offset -
        (3 *
            (MedicationDaySelectorMetrics.chipWidth +
                MedicationDaySelectorMetrics.dayGap));
  }

  /// Moves the strip after direct day selection so context remains visible.
  void _scrollToIndex(int index) {
    if (!_scrollController.hasClients) {
      return;
    }

    final maxOffset = _scrollController.position.maxScrollExtent;
    final targetOffset = _offsetForIndex(index).clamp(0.0, maxOffset);

    _scrollController.animateTo(
      targetOffset,
      duration: const Duration(milliseconds: 220),
      curve: Curves.easeOutCubic,
    );
  }

  /// Mirrors separator widths so manual scrolling and centering stay aligned.
  double _separatorWidthAfter(int index) {
    if (index >= _dates.length - 1) {
      return 0;
    }

    final currentDate = _dates[index];
    final nextDate = _dates[index + 1];

    if (currentDate.month != nextDate.month) {
      return MedicationDaySelectorMetrics.monthSeparatorWidth;
    }

    if (currentDate.weekday == DateTime.sunday) {
      return MedicationDaySelectorMetrics.weekGap;
    }

    return MedicationDaySelectorMetrics.dayGap;
  }

  /// Scrolls by roughly one week when the side arrow buttons are tapped.
  void _scrollByDirection(int direction) {
    if (!_scrollController.hasClients) {
      return;
    }

    final weekOffset =
        7 *
            (MedicationDaySelectorMetrics.chipWidth +
                MedicationDaySelectorMetrics.dayGap) +
        MedicationDaySelectorMetrics.weekGap;
    final maxOffset = _scrollController.position.maxScrollExtent;
    final targetOffset = (_scrollController.offset + direction * weekOffset)
        .clamp(0.0, maxOffset);

    _scrollController.animateTo(
      targetOffset,
      duration: const Duration(milliseconds: 220),
      curve: Curves.easeOutCubic,
    );
  }
}
