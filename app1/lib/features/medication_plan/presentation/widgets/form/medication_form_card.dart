import 'package:app1/core/widgets/careena_action_buttons.dart';
import 'package:app1/core/themes/app_colors.dart';
import 'package:flutter/material.dart';

import '../../../data/demo_medication_catalog.dart';
import '../../../data/medication_catalog_item.dart';
import '../../../data/medication_schedule.dart';
import 'dose_unit_autocomplete_field.dart';
import 'medication_catalog_autocomplete_field.dart';
import 'medication_catalog_details.dart';
import 'medication_frequency_field.dart';
import 'time_selector.dart';

/// Form card for entering medication name, dose, time, and reminder state.
class MedicationFormCard extends StatelessWidget {
  final GlobalKey<FormState> formKey;
  final TextEditingController nameController;
  final FocusNode nameFocusNode;
  final TextEditingController doseAmountController;
  final TextEditingController doseUnitController;
  final TimeOfDay selectedTime;
  final TimeOfDay secondSelectedTime;
  final MedicationFrequency frequency;
  final bool remindersEnabled;
  final MedicationCatalogItem? selectedCatalogItem;
  final ValueChanged<MedicationCatalogItem> onCatalogItemSelected;
  final VoidCallback onTimeTap;
  final VoidCallback onSecondTimeTap;
  final ValueChanged<MedicationFrequency> onFrequencyChanged;
  final ValueChanged<bool> onReminderChanged;
  final VoidCallback onCancel;
  final VoidCallback onSubmit;

  const MedicationFormCard({
    super.key,
    required this.formKey,
    required this.nameController,
    required this.nameFocusNode,
    required this.doseAmountController,
    required this.doseUnitController,
    required this.selectedTime,
    required this.secondSelectedTime,
    required this.frequency,
    required this.remindersEnabled,
    required this.selectedCatalogItem,
    required this.onCatalogItemSelected,
    required this.onTimeTap,
    required this.onSecondTimeTap,
    required this.onFrequencyChanged,
    required this.onReminderChanged,
    required this.onCancel,
    required this.onSubmit,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: colorScheme.surface,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: isDarkMode
              ? colorScheme.outlineVariant.withValues(alpha: 0.55)
              : AppColors.careenaBorder,
        ),
      ),
      child: Form(
        key: formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    'Neues Medikament',
                    style: TextStyle(
                      color: colorScheme.onSurface,
                      fontSize: 18,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
                CareenaIconActionButton.close(
                  tooltip: 'Abbrechen',
                  onPressed: onCancel,
                ),
              ],
            ),
            const SizedBox(height: 14),
            MedicationCatalogAutocompleteField(
              controller: nameController,
              focusNode: nameFocusNode,
              optionsBuilder: DemoMedicationCatalog.search,
              onSelected: onCatalogItemSelected,
              validator: _requiredMedicationName,
            ),
            if (selectedCatalogItem != null) ...[
              const SizedBox(height: 12),
              MedicationCatalogDetails(item: selectedCatalogItem!),
            ],
            const SizedBox(height: 12),
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  child: TextFormField(
                    controller: doseAmountController,
                    keyboardType: const TextInputType.numberWithOptions(
                      decimal: true,
                    ),
                    textInputAction: TextInputAction.next,
                    decoration: const InputDecoration(
                      labelText: 'Dosis',
                      hintText: 'z. B. 5, 1/2, ...',
                      prefixIcon: Icon(Icons.straighten),
                    ),
                    validator: _requiredDoseAmount,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: DoseUnitAutocompleteField(
                    controller: doseUnitController,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            MedicationFrequencyField(
              value: frequency,
              onChanged: onFrequencyChanged,
            ),
            const SizedBox(height: 12),
            TimeSelector(
              label: frequency == MedicationFrequency.twiceDaily
                  ? 'Erste Einnahme'
                  : 'Wann?',
              selectedTime: selectedTime,
              onTap: onTimeTap,
            ),
            if (frequency == MedicationFrequency.twiceDaily) ...[
              const SizedBox(height: 12),
              TimeSelector(
                label: 'Zweite Einnahme',
                selectedTime: secondSelectedTime,
                onTap: onSecondTimeTap,
              ),
            ],
            if (frequency == MedicationFrequency.weekly) ...[
              const SizedBox(height: 8),
              Text(
                'Wöchentliche Einnahmen werden ab dem Hinzufügetag an diesem Wochentag geplant.',
                style: TextStyle(
                  color: colorScheme.onSurfaceVariant,
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
            const SizedBox(height: 6),
            SwitchListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('Tägliche Erinnerung'),
              subtitle: Text(
                remindersEnabled
                    ? 'Push-Benachrichtigung ist aktiv'
                    : 'Ohne Push-Benachrichtigung speichern',
              ),
              value: remindersEnabled,
              activeThumbColor: AppColors.careenaTeal,
              onChanged: onReminderChanged,
            ),
            const SizedBox(height: 8),
            CareenaPrimaryIconButton(
              onPressed: onSubmit,
              icon: Icons.add,
              label: 'Eintrag speichern',
            ),
          ],
        ),
      ),
    );
  }

  /// Requires a medication name before saving the form.
  String? _requiredMedicationName(String? value) {
    if (value == null || value.trim().isEmpty) {
      return 'Bitte Medikament eintragen';
    }
    return null;
  }

  /// Requires the numeric dose amount before saving the form.
  String? _requiredDoseAmount(String? value) {
    if (value == null || value.trim().isEmpty) {
      return 'Bitte Menge eintragen';
    }
    return null;
  }
}