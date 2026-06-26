import 'package:app1/core/widgets/shared_day_selector.dart';
import 'package:flutter/material.dart';
import '../../data/symptom_entry.dart';
import 'symptom_add_button.dart';
import 'symptom_entry_list.dart';
import 'symptom_summary_card.dart';

/// Main symptom diary layout with date navigation, form, and daily history.
class SymptomDiaryContent extends StatelessWidget {
  final DateTime selectedDate;
  final DateTime today;
  final bool isLoading;
  final List<SymptomEntry> entries;
  final List<SymptomEntry> allEntries;
  final ValueChanged<DateTime> onDateSelected;
  final VoidCallback onAddSymptom;
  final ValueChanged<SymptomEntry> onDelete;

  const SymptomDiaryContent({
    super.key,
    required this.selectedDate,
    required this.today,
    required this.isLoading,
    required this.entries,
    required this.allEntries,
    required this.onDateSelected,
    required this.onAddSymptom,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Expanded(
          child: SingleChildScrollView(
            padding: const EdgeInsets.only(bottom: 16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                SharedDaySelector(
                  selectedDate: selectedDate,
                  today: today,
                  hasMarker: _hasEntryForDate,
                  isDateEnabled: (date) => !date.isAfter(today),
                  onDateSelected: onDateSelected,
                ),
                const SizedBox(height: 14),
                SymptomSummaryCard(entries: entries),
                const SizedBox(height: 16),
                SymptomEntryList(
                  isLoading: isLoading,
                  entries: entries,
                  onDelete: onDelete,
                ),
              ],
            ),
          ),
        ),
        Align(
          alignment: Alignment.centerRight,
          child: SymptomAddButton(onPressed: onAddSymptom),
        ),
      ],
    );
  }

  bool _hasEntryForDate(DateTime date) {
    return allEntries.any((entry) => isSameCalendarDay(entry.date, date));
  }
}
