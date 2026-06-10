import 'package:app1/core/themes/app_colors.dart';
import 'package:flutter/material.dart';

/// Small side arrow used for mouse-free day strip navigation.
class DayStripArrow extends StatelessWidget {
  final String tooltip;
  final IconData icon;
  final VoidCallback onPressed;

  const DayStripArrow({
    super.key,
    required this.tooltip,
    required this.icon,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return SizedBox(
      width: 32,
      child: IconButton(
        tooltip: tooltip,
        visualDensity: VisualDensity.compact,
        padding: EdgeInsets.zero,
        style: IconButton.styleFrom(
          backgroundColor: isDarkMode
              ? AppColors.darkElevatedSurface
              : AppColors.lightBackground,
          foregroundColor: isDarkMode
              ? AppColors.toolbarButtonBackgroundDark
              : AppColors.careenaDark,
        ),
        onPressed: onPressed,
        icon: Icon(icon, size: 22),
      ),
    );
  }
}