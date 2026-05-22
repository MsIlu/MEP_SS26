import 'package:flutter/material.dart';

import '../theme/warning_theme.dart';

/// Red divider used to visually separate emergency instructions.
class EmergencyDivider extends StatelessWidget {
  /// Whether to draw the stronger full-width divider below the header.
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
