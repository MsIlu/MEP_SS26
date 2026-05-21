import 'package:flutter/material.dart';

import '../theme/warning_copy.dart';
import '../theme/warning_theme.dart';
import '../view_models/emergency_reason.dart';

class ReasonBox extends StatelessWidget {
  final EmergencyReason reason;

  const ReasonBox({super.key, required this.reason});

  @override
  Widget build(BuildContext context) {
    if (!reason.hasDetails) return const SizedBox.shrink();

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: WarningDecorations.reasonBox,
      child: Text(
        '${WarningCopy.reasonPrefix}: ${reason.label}',
        style: WarningTextStyles.caption,
      ),
    );
  }
}
