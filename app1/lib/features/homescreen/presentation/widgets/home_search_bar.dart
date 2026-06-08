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
        : const Color.fromARGB(255, 255, 255, 255);

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

      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(30),

          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: isDarkMode ? 0.15 : 0.06),

              blurRadius: 10,

              offset: const Offset(0, 3),
            ),
          ],
        ),
        child: TextField(
          style: TextStyle(color: textColor),
          decoration: InputDecoration(
            hintText: 'Suchen...',
            hintStyle: TextStyle(color: hintColor),
            prefixIcon: Icon(Icons.search, color: iconColor),
            filled: true,
            fillColor: fillColor,

            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(30),
              borderSide: BorderSide(
                color: isDarkMode ? Colors.grey.shade700 : Colors.grey.shade300,
                width: 1.3,
              ),
            ),

            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(30),
              borderSide: BorderSide(color: AppColors.careenaTeal, width: 2),
            ),
          ),
        ),
      ),
    );
  }
}
