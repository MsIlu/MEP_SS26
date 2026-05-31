import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../../../../chatscreen/presentation/themes/app_colors.dart';

/// Required consent control for terms, privacy, health data, and emergency limits.
class ConsentCheckbox extends StatefulWidget {
  final bool value;
  final ValueChanged<bool> onChanged;

  const ConsentCheckbox({
    super.key,
    required this.value,
    required this.onChanged,
  });

  @override
  State<ConsentCheckbox> createState() => _ConsentCheckboxState();
}

class _ConsentCheckboxState extends State<ConsentCheckbox> {
  late final TapGestureRecognizer _termsRecognizer;
  late final TapGestureRecognizer _privacyRecognizer;

  @override
  void initState() {
    super.initState();
    _termsRecognizer = TapGestureRecognizer()
      ..onTap = () => _showInfoDialog(
        title: 'Nutzungsbedingungen',
        content:
            'Careena unterstützt dich beim Einordnen deiner Beschwerden und beim Vorbereiten weiterer Schritte. Die App ersetzt keine ärztliche Beratung, Diagnose oder Behandlung. Bitte gib nur korrekte Informationen ein und nutze die Hinweise verantwortungsvoll.',
      );
    _privacyRecognizer = TapGestureRecognizer()
      ..onTap = () => _showInfoDialog(
        title: 'Datenschutzhinweise',
        content:
            'Deine Angaben können Gesundheitsdaten enthalten. Sie werden im Prototyp genutzt, um personalisierte Unterstützung anzuzeigen. Eine spätere Produktversion muss Speicherung, Löschung, Zugriffsschutz und Rechtsgrundlage transparent regeln.',
      );
  }

  @override
  void dispose() {
    _termsRecognizer.dispose();
    _privacyRecognizer.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    final boxColor = isDarkMode ? colorScheme.surface : Colors.white;
    final borderColor = isDarkMode
        ? colorScheme.outlineVariant
        : AppColors.careenaBorder;

    final textColor = isDarkMode
        ? colorScheme.onSurfaceVariant
        : AppColors.careenaBody;

    final linkColor = isDarkMode
        ? AppColors.toolbarButtonBackgroundDark
        : AppColors.careenaPrimary;

    final baseStyle = GoogleFonts.nunito(
      height: 1.35,
      color: textColor,
    );

    final linkStyle = baseStyle.copyWith(
      color: linkColor,
      fontWeight: FontWeight.w800,
      decoration: TextDecoration.underline,
      decorationColor: linkColor,
    );

    return DecoratedBox(
      decoration: BoxDecoration(
        color: boxColor,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: borderColor),
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(16),
        onTap: () => widget.onChanged(!widget.value),
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Checkbox(
                value: widget.value,
                activeColor: AppColors.toolbarButtonBackgroundDark,
                onChanged: (checked) => widget.onChanged(checked ?? false),
              ),
              const SizedBox(width: 6),
              Expanded(
                child: RichText(
                  text: TextSpan(
                    style: baseStyle,
                    children: [
                      const TextSpan(text: 'Hiermit akzeptiere ich die '),
                      TextSpan(
                        text: 'Nutzungsbedingungen',
                        style: linkStyle,
                        recognizer: _termsRecognizer,
                      ),
                      const TextSpan(text: ' und '),
                      TextSpan(
                        text: 'Datenschutzhinweise',
                        style: linkStyle,
                        recognizer: _privacyRecognizer,
                      ),
                      const TextSpan(
                        text:
                            '. Ich willige ein, dass meine angegebenen Gesundheitsdaten zur Bereitstellung personalisierter Unterstützung verarbeitet werden. Mir ist bewusst, dass Careena keine ärztliche Diagnose stellt und in Notfällen der Notruf 112 oder medizinisches Fachpersonal zu kontaktieren ist.',
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _showInfoDialog({
    required String title,
    required String content,
  }) {
    return showDialog<void>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text(title),
          content: Text(content),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Schließen'),
            ),
          ],
        );
      },
    );
  }
}