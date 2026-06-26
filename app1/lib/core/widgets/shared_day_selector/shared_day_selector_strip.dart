import 'package:app1/core/themes/app_colors.dart';
import 'package:app1/core/widgets/shared_day_selector/shared_day_selector_date_utils.dart';
import 'package:app1/core/widgets/shared_day_selector/shared_day_selector_metrics.dart';
import 'package:flutter/material.dart';

/// Scrollable strip that owns date range and scroll positioning.
class SharedDaySelectorStrip extends StatefulWidget {
  final DateTime selectedDate;
  final DateTime today;
  final ValueChanged<DateTime> onDateSelected;
  final bool Function(DateTime date)? hasMarker;
  final bool Function(DateTime date)? isDateEnabled;

  const SharedDaySelectorStrip({
    super.key,
    required this.selectedDate,
    required this.today,
    required this.onDateSelected,
    this.hasMarker,
    this.isDateEnabled,
  });

  @override
  State<SharedDaySelectorStrip> createState() => _SharedDaySelectorStripState();
}

class _SharedDaySelectorStripState extends State<SharedDaySelectorStrip> {
  late final ScrollController _scrollController;
  late List<DateTime> _dates;

  @override
  void initState() {
    super.initState();
    _dates = buildSharedDayRange(widget.today);
    _scrollController = ScrollController(
      initialScrollOffset: _offsetForIndex(SharedDaySelectorMetrics.todayIndex),
    );
  }

  @override
  void didUpdateWidget(covariant SharedDaySelectorStrip oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (!isSameCalendarDay(oldWidget.today, widget.today)) {
      _dates = buildSharedDayRange(widget.today);
    }
    _scrollToSelectedDate(oldWidget.selectedDate);
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 102,
      child: Row(
        children: [
          _DayStripArrow(
            tooltip: 'Frühere Tage',
            icon: Icons.chevron_left,
            onPressed: () => _scrollByDirection(-1),
          ),
          Expanded(
            child: _FadedDayStrip(
              child: ListView.separated(
                controller: _scrollController,
                scrollDirection: Axis.horizontal,
                padding: const EdgeInsets.symmetric(horizontal: 2),
                itemCount: _dates.length,
                separatorBuilder: _buildSeparator,
                itemBuilder: _buildDayChip,
              ),
            ),
          ),
          _DayStripArrow(
            tooltip: 'Spätere Tage',
            icon: Icons.chevron_right,
            onPressed: () => _scrollByDirection(1),
          ),
        ],
      ),
    );
  }

  Widget _buildDayChip(BuildContext context, int index) {
    final date = _dates[index];
    final isEnabled = widget.isDateEnabled?.call(date) ?? true;

    return _SharedDayChip(
      date: date,
      isSelected: isSameCalendarDay(date, widget.selectedDate),
      isToday: isSameCalendarDay(date, widget.today),
      hasMarker: widget.hasMarker?.call(date) ?? false,
      isEnabled: isEnabled,
      onTap: isEnabled
          ? () {
              widget.onDateSelected(date);
              _scrollToIndex(index);
            }
          : null,
    );
  }

  Widget _buildSeparator(BuildContext context, int index) {
    final currentDate = _dates[index];
    final nextDate = _dates[index + 1];

    if (currentDate.month != nextDate.month) {
      return _MonthBoundarySeparator(monthDate: nextDate);
    }

    if (currentDate.weekday == DateTime.sunday) {
      return const SizedBox(width: SharedDaySelectorMetrics.weekGap);
    }

    return const SizedBox(width: SharedDaySelectorMetrics.dayGap);
  }

  void _scrollToSelectedDate(DateTime oldSelectedDate) {
    final selectedIndex = _dates.indexWhere(
      (date) => isSameCalendarDay(date, widget.selectedDate),
    );
    if (selectedIndex == -1 ||
        isSameCalendarDay(oldSelectedDate, widget.selectedDate)) {
      return;
    }

    WidgetsBinding.instance.addPostFrameCallback((_) {
      _scrollToIndex(selectedIndex);
    });
  }

  double _offsetForIndex(int index) {
    var offset = 0.0;
    for (var i = 0; i < index; i++) {
      offset += SharedDaySelectorMetrics.chipWidth + _separatorWidthAfter(i);
    }

    return offset -
        (3 *
            (SharedDaySelectorMetrics.chipWidth +
                SharedDaySelectorMetrics.dayGap));
  }

  void _scrollToIndex(int index) {
    if (!_scrollController.hasClients) return;

    final maxOffset = _scrollController.position.maxScrollExtent;
    final targetOffset = _offsetForIndex(index).clamp(0.0, maxOffset);

    _scrollController.animateTo(
      targetOffset,
      duration: const Duration(milliseconds: 220),
      curve: Curves.easeOutCubic,
    );
  }

  double _separatorWidthAfter(int index) {
    if (index >= _dates.length - 1) return 0;

    final currentDate = _dates[index];
    final nextDate = _dates[index + 1];

    if (currentDate.month != nextDate.month) {
      return SharedDaySelectorMetrics.monthSeparatorWidth;
    }

    if (currentDate.weekday == DateTime.sunday) {
      return SharedDaySelectorMetrics.weekGap;
    }

    return SharedDaySelectorMetrics.dayGap;
  }

  void _scrollByDirection(int direction) {
    if (!_scrollController.hasClients) return;

    final weekOffset =
        7 *
            (SharedDaySelectorMetrics.chipWidth +
                SharedDaySelectorMetrics.dayGap) +
        SharedDaySelectorMetrics.weekGap;
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

class _FadedDayStrip extends StatelessWidget {
  final Widget child;

  const _FadedDayStrip({required this.child});

  @override
  Widget build(BuildContext context) {
    return ShaderMask(
      shaderCallback: (bounds) {
        return const LinearGradient(
          begin: Alignment.centerLeft,
          end: Alignment.centerRight,
          colors: [
            AppColors.transparent,
            AppColors.black,
            AppColors.black,
            AppColors.transparent,
          ],
          stops: [0, 0.08, 0.92, 1],
        ).createShader(bounds);
      },
      blendMode: BlendMode.dstIn,
      child: child,
    );
  }
}

class _SharedDayChip extends StatelessWidget {
  final DateTime date;
  final bool isSelected;
  final bool isToday;
  final bool hasMarker;
  final bool isEnabled;
  final VoidCallback? onTap;

  const _SharedDayChip({
    required this.date,
    required this.isSelected,
    required this.isToday,
    required this.hasMarker,
    required this.isEnabled,
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
    final unselectedDayColor = isDarkMode
        ? colorScheme.onSurfaceVariant
        : AppColors.careenaDark;
    final dayColor = isSelected || isToday
        ? AppColors.careenaTeal
        : unselectedDayColor;
    final dateColor = isSelected ? AppColors.white : colorScheme.onSurface;

    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(18),
      child: Opacity(
        opacity: isEnabled ? 1.0 : 0.34,
        child: SizedBox(
          width: SharedDaySelectorMetrics.chipWidth,
          child: Column(
            mainAxisAlignment: MainAxisAlignment.end,
            children: [
              AnimatedOpacity(
                duration: const Duration(milliseconds: 160),
                opacity: isSelected ? 1 : 0,
                child: const Icon(
                  Icons.arrow_drop_down,
                  color: AppColors.careenaTeal,
                  size: 18,
                ),
              ),
              Text(
                formatSharedWeekday(date),
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
                        ? AppColors.careenaTeal
                        : AppColors.transparent,
                    width: 1.5,
                  ),
                ),
                child: Text(
                  '${date.day}',
                  style: TextStyle(
                    color: dateColor,
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ),
              const SizedBox(height: 4),
              AnimatedContainer(
                duration: const Duration(milliseconds: 160),
                width: hasMarker ? 6 : 0,
                height: 6,
                decoration: BoxDecoration(
                  color: hasMarker ? AppColors.careenaTeal : AppColors.transparent,
                  shape: BoxShape.circle,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _DayStripArrow extends StatelessWidget {
  final String tooltip;
  final IconData icon;
  final VoidCallback onPressed;

  const _DayStripArrow({
    required this.tooltip,
    required this.icon,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return IconButton(
      tooltip: tooltip,
      onPressed: onPressed,
      icon: Icon(icon),
      style: IconButton.styleFrom(
        foregroundColor: Theme.of(context).colorScheme.onSurfaceVariant,
      ),
    );
  }
}

class _MonthBoundarySeparator extends StatelessWidget {
  final DateTime monthDate;

  const _MonthBoundarySeparator({required this.monthDate});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return SizedBox(
      width: SharedDaySelectorMetrics.monthSeparatorWidth,
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
              formatSharedShortMonth(monthDate),
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
