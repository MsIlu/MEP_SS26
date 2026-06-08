import 'package:flutter/material.dart';
import '../../../chatscreen/presentation/themes/app_colors.dart';

/// Single tappable row in the home feature list.
class FunctionMenuTile extends StatelessWidget {
  /// Leading icon that represents the feature.
  final IconData icon;

  /// Feature label shown in the row.
  final String title;

  /// Background color behind the leading icon.
  final Color bgColor;

  /// Action executed when the tile is selected.
  final VoidCallback onTap;

  const FunctionMenuTile({
    super.key,
    required this.icon,
    required this.title,
    required this.bgColor,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    final borderColor = isDarkMode
        ? Colors.grey.shade700
        : Colors.grey.shade300;

    final iconBackgroundColor = isDarkMode ? const Color(0xFF222A35) : bgColor;

    final iconColor = isDarkMode
        ? AppColors.toolbarButtonBackgroundDark
        : AppColors.careenaDark;

    final titleColor = isDarkMode
        ? colorScheme.onSurface
        : AppColors.careenaDark;

    final trailingColor = isDarkMode
        ? AppColors.toolbarButtonBackgroundDark
        : AppColors.careenaTeal;

    return Container(
  margin: EdgeInsets.zero,
  decoration: BoxDecoration(
    border: Border.all(color: borderColor, width: 1.2),
    borderRadius: BorderRadius.circular(20),
    boxShadow: [
      BoxShadow(
        color: Colors.black.withValues(alpha: isDarkMode ? 0.20 : 0.08),
        blurRadius: 12,
        offset: const Offset(0, 4),
      ),
    ],
  ),
  child: Material(
    color: Theme.of(context).cardColor,
    borderRadius: BorderRadius.circular(20),
    child: ListTile(
      onTap: onTap,
      contentPadding: const EdgeInsets.symmetric(
        horizontal: 15,
        vertical: 5,
      ),
      minVerticalPadding: 12,
        leading: Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: iconBackgroundColor,
            borderRadius: BorderRadius.circular(12),
          ),
          child: Icon(icon, color: iconColor),
        ),
        title: Text(
          title,
          maxLines: 2,
          overflow: TextOverflow.ellipsis,
          style: TextStyle(fontWeight: FontWeight.bold, color: titleColor),
        ),
        trailing: Icon(Icons.chevron_right, color: trailingColor),
      ),
    ),
    );
  }
}
