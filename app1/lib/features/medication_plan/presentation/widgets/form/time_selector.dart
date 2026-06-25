import 'package:flutter/material.dart';

import '../../utils/medication_time_format.dart';

/// Read-only form control that opens the platform time picker.
class TimeSelector extends StatelessWidget {
  final TimeOfDay selectedTime;
  final String label;
  final VoidCallback onTap;

  const TimeSelector({
    super.key,
    required this.selectedTime,
    this.label = 'Wann?',
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: InputDecorator(
        decoration: const InputDecoration(
          prefixIcon: Icon(Icons.schedule),
        ).copyWith(labelText: label),
        child: Text(
          formatMedicationTime(selectedTime),
          style: TextStyle(
            color: Theme.of(context).colorScheme.onSurface,
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
    );
  }
}
