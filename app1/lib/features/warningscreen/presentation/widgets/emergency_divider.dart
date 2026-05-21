import 'package:flutter/material.dart';

import '../theme/warning_theme.dart';

class EmergencyDivider extends StatelessWidget {
  final bool strong;

  const EmergencyDivider({super.key, this.strong = false});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: strong
          ? EdgeInsets.zero
          : const EdgeInsets.only(left: 50, top: 10, bottom: 10),
      child: Divider(
        color: WarningColors.warningRed.withValues(alpha: strong ? 0.45 : 0.28),
        height: 1,
      ),
    );
  }
}
