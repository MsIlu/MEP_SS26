import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:app1/core/content/legal_texts.dart';
import 'package:app1/core/themes/app_colors.dart';

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
      ..onTap = () => _showLegalDialog(
        title: LegalTexts.termsTitle,
        subtitle: LegalTexts.termsSubtitle,
        paragraphs: LegalTexts.termsParagraphs,
      );
    _privacyRecognizer = TapGestureRecognizer()
      ..onTap = () => _showLegalDialog(
        title: LegalTexts.privacyTitle,
        subtitle: LegalTexts.privacySubtitle,
        paragraphs: LegalTexts.privacyParagraphs,
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

    final boxColor = isDarkMode ? colorScheme.surface : AppColors.white;
    final borderColor = isDarkMode
        ? colorScheme.outlineVariant
        : AppColors.careenaBorder;

    final textColor = isDarkMode
        ? colorScheme.onSurfaceVariant
        : AppColors.careenaBody;

    final linkColor = isDarkMode
        ? AppColors.toolbarButtonBackgroundDark
        : AppColors.careenaPrimary;

    final baseStyle = TextStyle(height: 1.35, color: textColor);

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

  Future<void> _showLegalDialog({
    required String title,
    required String subtitle,
    required List<String> paragraphs,
  }) {
    return showDialog<void>(
      context: context,
      builder: (context) {
        final colorScheme = Theme.of(context).colorScheme;
        final isDarkMode = Theme.of(context).brightness == Brightness.dark;
        final noticeColor = isDarkMode
            ? colorScheme.surfaceContainerHighest
            : AppColors.careenaNoteBackground;

        return AlertDialog(
          title: Text(title),
          content: SizedBox(
            width: 520,
            child: SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                mainAxisSize: MainAxisSize.min,
                children: [
                  DecoratedBox(
                    decoration: BoxDecoration(
                      color: noticeColor,
                      borderRadius: BorderRadius.circular(14),
                    ),
                    child: Padding(
                      padding: const EdgeInsets.all(14),
                      child: Text(
                        subtitle,
                        style: const TextStyle(fontWeight: FontWeight.w800),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  for (var index = 0; index < paragraphs.length; index++) ...[
                    _LegalParagraph(number: index + 1, text: paragraphs[index]),
                    if (index < paragraphs.length - 1)
                      const SizedBox(height: 14),
                  ],
                ],
              ),
            ),
          ),
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

class _LegalParagraph extends StatelessWidget {
  final int number;
  final String text;

  const _LegalParagraph({required this.number, required this.text});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        CircleAvatar(
          radius: 13,
          backgroundColor: AppColors.careenaTeal,
          foregroundColor: AppColors.white,
          child: Text(
            '$number',
            style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w800),
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: Text(
            text,
            style: TextStyle(color: colorScheme.onSurface, height: 1.35),
          ),
        ),
      ],
    );
  }
}