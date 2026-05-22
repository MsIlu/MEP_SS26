import 'package:flutter/material.dart';

import '../models/emergency_action.dart';
import '../theme/warning_copy.dart';
import '../theme/warning_theme.dart';
import 'emergency_divider.dart';
import 'highlighted_text.dart';

/// Renders the ordered emergency actions users should take immediately.
class EmergencyActionList extends StatelessWidget {
  const EmergencyActionList({super.key});

  /// Static actions keep the warning flow predictable and easy to audit.
  static const List<EmergencyAction> actions = [
    EmergencyAction(
      icon: Icons.phone_outlined,
      text: WarningCopy.callEmergency,
      highlightedText: '112',
    ),
    EmergencyAction(
      icon: Icons.local_hospital_outlined,
      text: WarningCopy.goToEmergencyRoom,
      highlightedText: 'Notaufnahme',
    ),
    EmergencyAction(
      icon: Icons.person_outline,
      text: WarningCopy.doNotStayAlone,
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        for (var index = 0; index < actions.length; index++) ...[
          _EmergencyActionRow(action: actions[index]),
          // Add separators only between rows, never after the final action.
          if (index < actions.length - 1) const EmergencyDivider(),
        ],
      ],
    );
  }
}

/// Single emergency action row with icon and optionally highlighted text.
class _EmergencyActionRow extends StatelessWidget {
  /// Action data rendered by this row.
  final EmergencyAction action;

  const _EmergencyActionRow({required this.action});

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        CircleAvatar(
          radius: 18,
          backgroundColor: WarningColors.warningRed.withValues(alpha: 0.1),
          child: Icon(action.icon, color: WarningColors.warningRed, size: 20),
        ),
        const SizedBox(width: 14),
        Expanded(
          child: Padding(
            padding: const EdgeInsets.only(top: 5),
            child: HighlightedText(
              text: action.text,
              highlightedText: action.highlightedText,
            ),
          ),
        ),
      ],
    );
  }
}
