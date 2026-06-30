import 'package:flutter/material.dart';

import 'add_medication_button.dart';
import 'medication_list_button.dart';

/// Bottom action row that frames the medication page with the top bar actions.
class MedicationBottomActions extends StatelessWidget {
  final VoidCallback onOpenMedicationList;
  final VoidCallback onAddMedication;

  const MedicationBottomActions({
    super.key,
    required this.onOpenMedicationList,
    required this.onAddMedication,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        MedicationListButton(onPressed: onOpenMedicationList),
        const Spacer(),
        AddMedicationButton(onPressed: onAddMedication),
      ],
    );
  }
}
