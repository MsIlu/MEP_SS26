import 'package:flutter/material.dart';

import '../../models/auth_review_item.dart';
import '../common/auth_buttons.dart';
import '../common/auth_layout.dart';
import '../review/auth_review_box.dart';
import '../review/consent_checkbox.dart';
import '../review/privacy_note.dart';

/// Final registration step: review, consent, and account creation.
class RegistrationReviewStep extends StatelessWidget {
  final List<AuthReviewItem> personalItems;
  final List<AuthReviewItem> healthItems;
  final bool hasAcceptedConsent;
  final ValueChanged<bool> onConsentChanged;
  final VoidCallback onEditPersonalData;
  final VoidCallback onEditHealthData;
  final VoidCallback onSubmit;

  const RegistrationReviewStep({
    super.key,
    required this.personalItems,
    required this.healthItems,
    required this.hasAcceptedConsent,
    required this.onConsentChanged,
    required this.onEditPersonalData,
    required this.onEditHealthData,
    required this.onSubmit,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const AuthSectionTitle('Überprüfe deine Angaben'),
        const SizedBox(height: 16),
        AuthReviewBox(
          title: 'Persönliche Daten',
          items: personalItems,
          onEdit: onEditPersonalData,
        ),
        const SizedBox(height: 12),
        AuthReviewBox(
          title: 'Gesundheitsangaben',
          items: healthItems,
          onEdit: onEditHealthData,
        ),
        const SizedBox(height: 18),
        const PrivacyNote(),
        const SizedBox(height: 14),
        ConsentCheckbox(value: hasAcceptedConsent, onChanged: onConsentChanged),
        const SizedBox(height: 24),
        CareenaButton(
          text: 'Konto erstellen',
          onPressed: hasAcceptedConsent ? onSubmit : null,
        ),
      ],
    );
  }
}
