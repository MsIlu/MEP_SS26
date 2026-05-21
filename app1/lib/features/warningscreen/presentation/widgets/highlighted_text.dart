import 'package:flutter/material.dart';

import '../theme/warning_theme.dart';

class HighlightedText extends StatelessWidget {
  final String text;
  final String? highlightedText;

  const HighlightedText({
    super.key,
    required this.text,
    required this.highlightedText,
  });

  @override
  Widget build(BuildContext context) {
    final highlight = highlightedText;

    if (highlight == null || !text.contains(highlight)) {
      return Text(text, style: WarningTextStyles.body);
    }

    final parts = text.split(highlight);

    return RichText(
      text: TextSpan(
        style: WarningTextStyles.body,
        children: [
          TextSpan(text: parts.first),
          TextSpan(text: highlight, style: WarningTextStyles.highlight),
          TextSpan(text: parts.length > 1 ? parts.last : ''),
        ],
      ),
    );
  }
}