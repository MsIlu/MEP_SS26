import 'package:flutter/material.dart';

import '../../../chatscreen/data/models/chat_response_model.dart';
import '../theme/warning_copy.dart';
import '../theme/warning_layout.dart';
import '../theme/warning_theme.dart';
import '../view_models/emergency_reason.dart';
import 'emergency_action_list.dart';
import 'emergency_call_button.dart';
import 'emergency_divider.dart';
import 'reason_box.dart';
import 'section_title.dart';
import 'warning_header.dart';

/// Main warning card that groups urgent copy, actions, details, and call CTA.
class EmergencyCard extends StatelessWidget {
  /// Backend response that triggered the emergency flow.
  final ChatResponse response;

  const EmergencyCard({super.key, required this.response});

  @override
  Widget build(BuildContext context) {
    // Convert backend metadata into a compact, user-facing reason before
    // composing the visual warning card.
    final reason = EmergencyReason.fromResponse(response);

    return Semantics(
      label: WarningCopy.semanticEmergencyLabel,
      child: Container(
        width: double.infinity,
        padding: WarningLayout.cardPadding,
        decoration: WarningDecorations.emergencyCard(context),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const WarningHeader(),
            const SizedBox(height: 18),
            const EmergencyDivider(strong: true),
            const SizedBox(height: 12),
            const SectionTitle(WarningCopy.actionTitle),
            const SizedBox(height: 14),
            const EmergencyActionList(),
            if (reason.hasDetails) ...[
              const SizedBox(height: 18),
              ReasonBox(reason: reason),
            ],
            const SizedBox(height: 22),
            const EmergencyCallButton(),
          ],
        ),
      ),
    );
  }
}
