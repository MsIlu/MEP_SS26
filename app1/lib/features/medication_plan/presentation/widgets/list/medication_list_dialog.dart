import 'package:app1/core/widgets/careena_action_buttons.dart';
import 'package:flutter/material.dart';

import '../../../data/medication_entry.dart';
import 'medication_entry_section.dart';

/// Dialog content for reviewing, deleting, and updating saved medications.
class MedicationListDialog extends StatelessWidget {
  final bool isLoading;
  final List<MedicationEntry> entries;
  final VoidCallback onAdd;
  final VoidCallback onClose;
  final void Function(MedicationEntry entry, bool remindersEnabled)
  onToggleReminder;
  final ValueChanged<MedicationEntry> onEdit;
  final ValueChanged<MedicationEntry> onDelete;

  const MedicationListDialog({
    super.key,
    required this.isLoading,
    required this.entries,
    required this.onAdd,
    required this.onClose,
    required this.onToggleReminder,
    required this.onEdit,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _MedicationListDialogHeader(onAdd: onAdd, onClose: onClose),
        const SizedBox(height: 10),
        Flexible(
          child: SingleChildScrollView(
            child: MedicationEntrySection(
              isLoading: isLoading,
              entries: entries,
              onToggleReminder: onToggleReminder,
              onEdit: onEdit,
              onDelete: onDelete,
              showTitle: false,
            ),
          ),
        ),
      ],
    );
  }
}

class _MedicationListDialogHeader extends StatelessWidget {
  final VoidCallback onAdd;
  final VoidCallback onClose;

  const _MedicationListDialogHeader({
    required this.onAdd,
    required this.onClose,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Row(
      children: [
        Expanded(
          child: Text(
            'Meine Medikamente',
            style: TextStyle(
              color: colorScheme.onSurface,
              fontSize: 18,
              fontWeight: FontWeight.w800,
            ),
          ),
        ),
        CareenaIconActionButton(
          tooltip: 'Medikament hinzufügen',
          icon: Icons.add,
          onPressed: onAdd,
        ),
        CareenaIconActionButton.close(tooltip: 'Schließen', onPressed: onClose),
      ],
    );
  }
}
