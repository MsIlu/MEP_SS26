import 'package:app1/core/content/legal_texts.dart';
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
        'Bei Fragen zur Bedienung, zu gespeicherten Daten oder zu technischen Problemen erreichst du das Team MedBitAid per E-Mail unter support@medbitaid.de.',
        'Bitte sende keine akuten medizinischen Notfälle per E-Mail. In lebensbedrohlichen Situationen oder bei starken Warnzeichen wähle sofort den Notruf 112.',
        'Careena ist ein Studienprojekt und unterstützt bei der strukturierten Erfassung von Beschwerden. Die App ersetzt keine ärztliche Untersuchung, Diagnose oder Behandlung.',
      ];

  const SettingsTextPage.privacy({super.key})
    : title = LegalTexts.privacyTitle,
      subtitle = LegalTexts.privacySubtitle,
      icon = SettingsIcons.privacy,
      paragraphs = LegalTexts.privacyParagraphs;

  const SettingsTextPage.terms({super.key})
    : title = LegalTexts.termsTitle,
      subtitle = LegalTexts.termsSubtitle,
      icon = Icons.assignment_outlined,
      paragraphs = LegalTexts.termsParagraphs;

  const SettingsTextPage.accessibility({super.key})
    : title = 'Barrierefreiheit',
      subtitle = 'Bedienung und Lesbarkeit.',
      icon = Icons.accessible_forward,
      paragraphs = const [
        'Careena soll auch dann gut nutzbar sein, wenn Texte schwer lesbar sind oder kleine Bedienelemente die Bedienung erschweren.',
        'Die größere Ansicht vergrößert Schrift, Schaltflächen und wichtige Bedienelemente. Außerdem werden einige Ansichten ruhiger dargestellt, damit Inhalte leichter erkennbar bleiben.',
        'Die App unterstützt Tastaturfokus und gut sichtbare Hauptnavigation. Des Weiteren besteht im Chat die Möglichkeit einer Spracheingabe und die App ist Screenreader-kompatibel. Wenn dir Barrieren auffallen, melde sie bitte an support@medbitaid.de.',
      ];

  const SettingsTextPage.imprint({super.key})
    : title = 'Impressum',
      subtitle = 'Angaben zum Anbieter.',
      icon = Icons.info_outline,
      paragraphs = const [
        'Careena ist ein Studienprojekt des Teams MedBitAid.',
        'Teamname: MedBitAid',
        'Kontakt: support@medbitaid.de',
        'Verantwortlich für Konzept, Umsetzung und Inhalte im Rahmen der Projektabgabe ist das Projektteam MedBitAid.',
        'Diese App ist ein Prototyp für Ausbildungs- und Demonstrationszwecke. Sie ist nicht als Medizinprodukt zertifiziert und nicht für den produktiven medizinischen Einsatz bestimmt.',
        'Medizinischer Hinweis: Careena stellt keine Diagnose, ersetzt keine ärztliche Beratung und übernimmt keine Notfallversorgung. Bei akuten Beschwerden oder Unsicherheit wende dich an medizinisches Fachpersonal. In Notfällen gilt der Notruf 112.',
      ];

  const SettingsTextPage.about({super.key})
    : title = 'Über Careena',
      subtitle = 'Informationen und App-Version.',
      icon = Icons.phone_android,
      paragraphs = const [
        'Careena ist eine App des Teams MedBitAid. Sie unterstützt dabei, Beschwerden strukturiert zu beschreiben, Symptome über die Zeit zu dokumentieren und mögliche nächste Schritte besser vorzubereiten.',
        'Die App richtet sich an Nutzerinnen und Nutzer, die ihre gesundheitlichen Informationen übersichtlich erfassen möchten. Careena kann Hinweise geben, ersetzt aber keine medizinische Diagnose oder Behandlung.',
        'Projektstatus: Studienprojekt / Prototyp',
        'Version: 1.0',
        'Kontakt: support@medbitaid.de',
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
