import 'package:flutter/material.dart';

import '../theme/warning_copy.dart';
import '../theme/warning_theme.dart';

/// Reminder that the warning screen is not a medical diagnosis.
class NoDiagnosisInfoBox extends StatelessWidget {
  const NoDiagnosisInfoBox({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: WarningDecorations.infoBox,
      child: const Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.info_outline, color: WarningColors.teal, size: 20),
          SizedBox(width: 10),
          Expanded(
            child: Text(
              WarningCopy.noDiagnosis,
              style: TextStyle(
                color: WarningColors.darkText,
                fontSize: 12,
                height: 1.35,
              ),
            ),
          ),
        ],
      ),
    );
  }
}