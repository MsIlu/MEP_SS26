import 'package:flutter/material.dart';
import '../theme/warning_theme.dart';

/// Text widget that highlights one important substring when it is present.
class HighlightedText extends StatelessWidget {
  /// Full text to render.
  final String text;

  /// Optional exact substring that should use the warning highlight style.
  final String? highlightedText;

  const HighlightedText({
    super.key,
    required this.text,
    required this.highlightedText,
  });

  @override
  Widget build(BuildContext context) {
    final highlight = highlightedText;
    final bodyStyle = WarningTextStyles.bodyFor(context);

    // Fall back to plain body text when there is nothing safe to highlight.
    if (highlight == null || !text.contains(highlight)) {
      return Text(text, style: bodyStyle);
    }

    // Splitting keeps the highlighted substring styleable while preserving the
    // surrounding sentence in the default body style.
    final parts = text.split(highlight);

    return RichText(
      text: TextSpan(
        style: bodyStyle,
        children: [
          TextSpan(text: parts.first),
          TextSpan(text: highlight, style: WarningTextStyles.highlight),
          TextSpan(text: parts.length > 1 ? parts.last : ''),
        ],
      ),
    );
  }
}