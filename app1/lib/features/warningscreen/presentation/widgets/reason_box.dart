import 'package:flutter/material.dart';

import '../theme/warning_copy.dart';
import '../theme/warning_theme.dart';
import '../view_models/emergency_reason.dart';

/// Optional box that explains which backend metadata triggered the warning.
class ReasonBox extends StatelessWidget {
  /// Presentation model containing displayable red-flag details.
  final EmergencyReason reason;

  const ReasonBox({super.key, required this.reason});

  @override
  Widget build(BuildContext context) {
    // Keep the card clean when the backend did not provide displayable details.
    if (!reason.hasDetails) return const SizedBox.shrink();

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: WarningDecorations.reasonBox(context),
      child: Text(
        '${WarningCopy.reasonPrefix}: ${reason.label}',
        style: WarningTextStyles.caption,
      ),
    );
  }
}