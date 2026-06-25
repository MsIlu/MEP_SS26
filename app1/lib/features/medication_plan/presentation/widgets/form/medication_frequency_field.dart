import 'package:flutter/material.dart';

import '../../../data/medication_schedule.dart';

/// Reusable form field for selecting how often a medication is taken.
class MedicationFrequencyField extends StatelessWidget {
  final MedicationFrequency value;
  final ValueChanged<MedicationFrequency> onChanged;

  const MedicationFrequencyField({
    super.key,
    required this.value,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return DropdownButtonFormField<MedicationFrequency>(
      initialValue: value,
      decoration: const InputDecoration(
        labelText: 'Einnahmehäufigkeit',
        prefixIcon: Icon(Icons.repeat),
      ),
      items: MedicationFrequency.values.map((frequency) {
        return DropdownMenuItem(value: frequency, child: Text(frequency.label));
      }).toList(),
      onChanged: (selectedFrequency) {
        if (selectedFrequency != null) {
          onChanged(selectedFrequency);
        }
      },
    );
  }
}