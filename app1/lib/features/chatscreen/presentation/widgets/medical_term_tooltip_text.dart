import 'package:app1/core/themes/app_colors.dart';
import 'package:flutter/material.dart';

import '../../utils/medical_terms.dart';

class MedicalTermTooltipText extends StatelessWidget {
  final String text;
  final bool enabled;
  final TextStyle style;

  const MedicalTermTooltipText({
    super.key,
    required this.text,
    required this.enabled,
    required this.style,
  });

  @override
  Widget build(BuildContext context) {
    final matches = enabled ? MedicalTerms.matchesIn(text) : const [];

    if (matches.isEmpty) {
      return Text(text, style: style);
    }

    final spans = <InlineSpan>[];
    var cursor = 0;

    for (final match in matches) {
      if (cursor < match.start) {
        spans.add(TextSpan(text: text.substring(cursor, match.start)));
      }

      spans.add(_buildTooltipSpan(match));
      cursor = match.end;
    }

    if (cursor < text.length) {
      spans.add(TextSpan(text: text.substring(cursor)));
    }

    return Text.rich(TextSpan(style: style, children: spans));
  }

  WidgetSpan _buildTooltipSpan(MedicalTermMatch match) {
    final matchedText = text.substring(match.start, match.end);

    return WidgetSpan(
      alignment: PlaceholderAlignment.baseline,
      baseline: TextBaseline.alphabetic,
      child: Tooltip(
        message: '${match.term.term}: ${match.term.explanation}',
        triggerMode: TooltipTriggerMode.tap,
        showDuration: const Duration(seconds: 6),
        child: Semantics(
          button: true,
          label: 'Fachbegriff ${match.term.term}. ${match.term.explanation}',
          child: Text(
            matchedText,
            style: style.copyWith(
              color: AppColors.careenaTeal,
              fontWeight: FontWeight.w900,
              decoration: TextDecoration.underline,
              decorationColor: AppColors.careenaTeal,
              decorationThickness: 1.5,
            ),
          ),
        ),
      ),
    );
  }
}
