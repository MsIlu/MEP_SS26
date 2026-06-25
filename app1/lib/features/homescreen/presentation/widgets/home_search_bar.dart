import 'package:flutter/material.dart';
import 'package:app1/core/themes/app_colors.dart';

/// Search field shown below the home hero card.
class HomeSearchBar extends StatelessWidget {
  /// Whether the field should use the narrow phone spacing.
  final bool isCompact;
  final Key? guideTargetKey;

  const HomeSearchBar({
    super.key,
    required this.isCompact,
    this.guideTargetKey,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    final fillColor = isDarkMode
        ? AppColors.darkElevatedSurface
        : AppColors.lightCard;

    final borderColor = isDarkMode
        ? colorScheme.outlineVariant
        : AppColors.careenaBorder;

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
        key: guideTargetKey,
        style: TextStyle(color: textColor),
        decoration: InputDecoration(
          hintText: 'Suchen...',
          hintStyle: TextStyle(color: hintColor),
          prefixIcon: Icon(Icons.search, color: iconColor),
          filled: true,
          fillColor: fillColor,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(30),
            borderSide: BorderSide(color: borderColor),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(30),
            borderSide: BorderSide(color: borderColor),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(30),
            borderSide: const BorderSide(
              color: AppColors.careenaTeal,
              width: 2,
            ),
          ),
        ),
      ),
    );
  }
}
