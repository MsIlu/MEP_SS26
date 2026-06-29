import 'package:flutter/material.dart';

import '../screens/settings_text_page.dart';
import 'settings_components.dart';

class SettingsInfoSection extends StatelessWidget {
  const SettingsInfoSection({super.key});

  @override
  Widget build(BuildContext context) {
    return const Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        SettingsSectionHeader(
          icon: Icons.help_outline,
          title: 'Hilfe und Informationen',
          subtitle: 'Alles Wichtige zu Careena.',
        ),
        SizedBox(height: 10),
        SettingsPanel(
          children: [
            SettingsLinkTile(
              icon: Icons.support_agent,
              title: 'Hilfe und Kontakt',
              description: 'Unterstützung bei Fragen',
              page: SettingsTextPage.help(),
            ),
            SettingsLinkTile(
              icon: Icons.privacy_tip_outlined,
              title: 'Datenschutz',
              description: 'Wie deine Daten geschützt werden',
              page: SettingsTextPage.privacy(),
            ),
            SettingsLinkTile(
              icon: Icons.accessible_forward,
              title: 'Barrierefreiheit',
              description: 'Bedienung und Rückmeldung',
              page: SettingsTextPage.accessibility(),
            ),
            SettingsLinkTile(
              icon: Icons.info_outline,
              title: 'Impressum',
              description: 'Angaben zum Anbieter',
              page: SettingsTextPage.imprint(),
            ),
            SettingsLinkTile(
              icon: Icons.phone_android,
              title: 'Über Careena',
              description: 'Informationen und App-Version',
              page: SettingsTextPage.about(),
            ),
          ],
        ),
      ],
    );
  }
}
