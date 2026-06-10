import 'package:app1/core/themes/app_colors.dart';
import 'package:flutter/material.dart';

import '../../../data/medication_entry.dart';
import '../../utils/medication_time_format.dart';

/// List tile for one saved medication and its reminder toggle.
class MedicationTile extends StatelessWidget {
  final MedicationEntry entry;
  final ValueChanged<bool> onToggleReminder;
  final VoidCallback onDelete;

  const MedicationTile({
    super.key,
    required this.entry,
    required this.onToggleReminder,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Container(
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
              Container(
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
              const SizedBox(width: 12),
              Expanded(
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
              IconButton(
                tooltip: 'Löschen',
                onPressed: onDelete,
                icon: const Icon(Icons.delete_outline),
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
                const SizedBox(width: 12),
                Switch(
                  value: entry.remindersEnabled,
                  activeThumbColor: AppColors.careenaTeal,
                  onChanged: onToggleReminder,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}