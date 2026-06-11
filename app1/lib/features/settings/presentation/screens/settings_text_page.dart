import 'package:flutter/material.dart';
import '../settings_icons.dart';
import '../widgets/settings_detail_scaffold.dart';

class SettingsTextPage extends StatelessWidget {
  final String title;
  final String subtitle;
  final IconData icon;
  final List<String> paragraphs;

  const SettingsTextPage({
    super.key,
    required this.title,
    required this.subtitle,
    required this.icon,
    required this.paragraphs,
  });

  const SettingsTextPage.help({super.key})
    : title = 'Hilfe und Kontakt',
      subtitle = 'Unterstützung bei Fragen zur App.',
      icon = SettingsIcons.help,
      paragraphs = const [
        'Bei Fragen zur Bedienung hilft dir unser Support weiter.',
        'In medizinischen Notfällen wende dich bitte direkt an den Rettungsdienst.',
      ];

  const SettingsTextPage.privacy({super.key})
    : title = 'Datenschutz',
      subtitle = 'Wie deine Daten geschützt werden.',
      icon = SettingsIcons.privacy,
      paragraphs = const [
        'Gesundheitsdaten werden vertraulich behandelt und nur für die vorgesehenen Funktionen verwendet.',
      ];

  const SettingsTextPage.accessibility({super.key})
    : title = 'Barrierefreiheit',
      subtitle = 'Bedienung und Rückmeldung.',
      icon = Icons.accessible_forward,
      paragraphs = const [
        'Die einfache Ansicht vergrößert Bedienelemente und reduziert Ablenkungen.',
      ];

  const SettingsTextPage.imprint({super.key})
    : title = 'Impressum',
      subtitle = 'Angaben zum Anbieter.',
      icon = Icons.info_outline,
      paragraphs = const [
        'MedBitAid',
        'Weitere Anbieterangaben werden vor der Veröffentlichung ergänzt.',
      ];

  const SettingsTextPage.about({super.key})
    : title = 'Über Careena',
      subtitle = 'Informationen und App-Version.',
      icon = Icons.phone_android,
      paragraphs = const [
        'Careena unterstützt bei der strukturierten Erfassung gesundheitlicher Informationen.',
        'Version 1.0',
      ];

  @override
  Widget build(BuildContext context) {
    return SettingsDetailScaffold(
      title: title,
      subtitle: subtitle,
      icon: icon,
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              for (var index = 0; index < paragraphs.length; index++) ...[
                Text(paragraphs[index]),
                if (index < paragraphs.length - 1) const SizedBox(height: 16),
              ],
            ],
          ),
        ),
      ),
    );
  }
}