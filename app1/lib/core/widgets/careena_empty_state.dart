import 'package:app1/core/themes/app_colors.dart';
import 'package:flutter/material.dart';

/// Shared empty state for feature pages and empty list sections.
class CareenaEmptyState extends StatelessWidget {
  final IconData icon;
  final String title;
  final String message;
  final double maxWidth;
  final double iconSize;
  final EdgeInsetsGeometry padding;

  const CareenaEmptyState({
    super.key,
    required this.icon,
    required this.title,
    required this.message,
    this.maxWidth = 280,
    this.iconSize = 64,
    this.padding = const EdgeInsets.symmetric(vertical: 24),
  });

  @override
  Widget build(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    final accentColor = isDarkMode
        ? AppColors.careenaAccentOnDark
        : AppColors.careenaTeal;
    final messageColor = accentColor.withValues(alpha: isDarkMode ? 0.9 : 0.75);

    return LayoutBuilder(
      builder: (context, constraints) {
        final hasBoundedHeight =
            constraints.hasBoundedHeight && constraints.maxHeight.isFinite;

        final content = Center(
          child: Padding(
            padding: padding,
            child: ConstrainedBox(
              constraints: BoxConstraints(maxWidth: maxWidth),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    icon,
                    color: accentColor.withValues(alpha: 0.95),
                    size: iconSize,
                  ),
                  const SizedBox(height: 16),
                  Text(
                    title,
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: accentColor,
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                      height: 1.3,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    message,
                    textAlign: TextAlign.center,
                    style: TextStyle(color: messageColor, height: 1.35),
                  ),
                ],
              ),
            ),
          ),
        );

        if (!hasBoundedHeight) return content;

        // Keep bounded empty sections vertically centered without risking overflow.
        return SingleChildScrollView(
          child: ConstrainedBox(
            constraints: BoxConstraints(minHeight: constraints.maxHeight),
            child: content,
          ),
        );
      },
    );
  }
}