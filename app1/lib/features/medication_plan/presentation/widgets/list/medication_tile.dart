import 'package:app1/core/themes/app_colors.dart';
import 'package:flutter/material.dart';

import '../../../data/medication_entry.dart';
import '../../utils/medication_time_format.dart';

/// List tile for one saved medication and its reminder toggle.
class MedicationTile extends StatelessWidget {
  final MedicationEntry entry;
  final ValueChanged<bool> onToggleReminder;
  final VoidCallback onEdit;
  final VoidCallback onDelete;

  const MedicationTile({
    super.key,
    required this.entry,
    required this.onToggleReminder,
    required this.onEdit,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    final medicationLabel = _semanticLabel();

    return Semantics(
      container: true,
      label: medicationLabel,
      child: Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: colorScheme.surface,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: isDarkMode
                ? colorScheme.outlineVariant.withValues(alpha: 0.55)
                : AppColors.careenaBorder,
          ),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                ExcludeSemantics(
                  child: Container(
                    width: 46,
                    height: 46,
                    decoration: BoxDecoration(
                      color: isDarkMode
                          ? AppColors.darkElevatedSurface
                          : AppColors.careenaInfoBorder,
                      borderRadius: BorderRadius.circular(14),
                    ),
                    child: Icon(
                      Icons.medication_liquid_outlined,
                      color: isDarkMode
                          ? AppColors.toolbarButtonBackgroundDark
                          : AppColors.careenaDark,
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: ExcludeSemantics(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          entry.name,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: TextStyle(
                            color: colorScheme.onSurface,
                            fontSize: 16,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                        const SizedBox(height: 3),
                        Text(
                          '${entry.dose} - ${entry.frequency.label} um ${formatMedicationTimes(entry.intakeTimes)}',
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                          style: TextStyle(color: colorScheme.onSurfaceVariant),
                        ),
                        if (entry.catalogItem != null) ...[
                          const SizedBox(height: 3),
                          Text(
                            entry.catalogItem!.activeSubstance,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: TextStyle(
                              color: colorScheme.onSurfaceVariant,
                              fontSize: 12,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                ),
                Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Semantics(
                      button: true,
                      label: '${entry.name} bearbeiten',
                      child: ExcludeSemantics(
                        child: IconButton(
                          tooltip: '${entry.name} bearbeiten',
                          onPressed: onEdit,
                          icon: const Icon(Icons.edit_outlined),
                        ),
                      ),
                    ),
                    Semantics(
                      button: true,
                      label: '${entry.name} löschen',
                      child: ExcludeSemantics(
                        child: IconButton(
                          tooltip: '${entry.name} löschen',
                          onPressed: onDelete,
                          icon: const Icon(Icons.delete_outline),
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 10),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(
                color: isDarkMode
                    ? AppColors.darkElevatedSurface
                    : AppColors.careenaBubbleBackground,
                borderRadius: BorderRadius.circular(14),
              ),
              child: Row(
                children: [
                  Expanded(
                    child: ExcludeSemantics(
                      child: Text(
                        'Benachrichtigungen aktivieren',
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        softWrap: false,
                        style: TextStyle(
                          color: colorScheme.onSurface,
                          fontSize: 13,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Semantics(
                    label: 'Benachrichtigungen für ${entry.name}',
                    toggled: entry.remindersEnabled,
                    child: Switch(
                      value: entry.remindersEnabled,
                      activeThumbColor: AppColors.careenaTeal,
                      onChanged: onToggleReminder,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _semanticLabel() {
    final parts = <String>[
      'Medikament: ${entry.name}',
      'Dosis: ${entry.dose}',
      entry.frequency.label,
      'Einnahmezeit ${formatMedicationTimes(entry.intakeTimes)}',
    ];
    if (entry.catalogItem != null) {
      parts.add('Wirkstoff: ${entry.catalogItem!.activeSubstance}');
    }
    parts.add(
      entry.remindersEnabled
          ? 'Benachrichtigungen aktiviert'
          : 'Benachrichtigungen deaktiviert',
    );
    return parts.join('. ');
  }
}
