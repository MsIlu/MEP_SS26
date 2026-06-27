import 'package:app1/core/themes/app_colors.dart';
import 'package:flutter/material.dart';

import '../../../data/medication_catalog_item.dart';

/// Compact metadata panel for a selected catalog medication.
class MedicationCatalogDetails extends StatelessWidget {
  final MedicationCatalogItem item;

  const MedicationCatalogDetails({super.key, required this.item});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Container(
      constraints: const BoxConstraints(minHeight: 56),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: isDarkMode
            ? AppColors.darkElevatedSurface
            : AppColors.careenaNoteBackground,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: isDarkMode
              ? colorScheme.outlineVariant.withValues(alpha: 0.55)
              : AppColors.careenaInfoBorder,
        ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          const Icon(Icons.info_outline, color: AppColors.careenaTeal),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              '${item.activeSubstance} • ${item.strength} • ${item.dosageForm}',
              textAlign: TextAlign.left,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
              style: TextStyle(
                color: colorScheme.onSurface,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
