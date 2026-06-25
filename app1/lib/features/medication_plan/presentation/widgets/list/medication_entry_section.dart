import 'package:flutter/material.dart';

import '../../../data/medication_entry.dart';
import '../common/empty_medication_state.dart';
import 'medication_tile.dart';

/// Renders loading, empty, and populated states for saved medications.
class MedicationEntrySection extends StatelessWidget {
  final bool isLoading;
  final List<MedicationEntry> entries;
  final void Function(MedicationEntry entry, bool remindersEnabled)
  onToggleReminder;
  final ValueChanged<MedicationEntry> onEdit;
  final ValueChanged<MedicationEntry> onDelete;
  final bool showTitle;

  const MedicationEntrySection({
    super.key,
    required this.isLoading,
    required this.entries,
    required this.onToggleReminder,
    required this.onEdit,
    required this.onDelete,
    this.showTitle = true,
  });

  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (entries.isEmpty) {
      return const EmptyMedicationState();
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (showTitle) ...[
          Text(
            'Meine Medikamente',
            style: TextStyle(
              color: Theme.of(context).colorScheme.onSurface,
              fontSize: 16,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 10),
        ],
        ...entries.map(
          (entry) => Padding(
            padding: const EdgeInsets.only(bottom: 10),
            child: MedicationTile(
              entry: entry,
              onToggleReminder: (value) => onToggleReminder(entry, value),
              onEdit: () => onEdit(entry),
              onDelete: () => onDelete(entry),
            ),
          ),
        ),
      ],
    );
  }
}
