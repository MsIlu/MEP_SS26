import 'package:flutter/material.dart';

import '../../../chatscreen/presentation/themes/app_colors.dart';

/// Search field shown below the home hero card.
class HomeSearchBar extends StatelessWidget {
  /// Whether the field should use the narrow phone spacing.
  final bool isCompact;

  const HomeSearchBar({super.key, required this.isCompact});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    final fillColor = isDarkMode
        ? const Color(0xFF222A35)
        : AppColors.background;

    final iconColor = isDarkMode
        ? colorScheme.onSurfaceVariant
        : AppColors.careenaDark;

    final textColor = isDarkMode
        ? colorScheme.onSurface
        : AppColors.careenaDark;

    final hintColor = isDarkMode
        ? colorScheme.onSurfaceVariant
        : AppColors.careenaBody;

    return Padding(
      padding: EdgeInsets.symmetric(
        horizontal: isCompact ? 16 : 20,
        vertical: 15,
      ),
      child: TextField(
        style: TextStyle(color: textColor),
        decoration: InputDecoration(
          hintText: 'Suchen...',
          hintStyle: TextStyle(color: hintColor),
          prefixIcon: Icon(Icons.search, color: iconColor),
          filled: true,
          fillColor: fillColor,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(30),
            borderSide: BorderSide.none,
          ),
        ),
      ),
    );
  }
}
