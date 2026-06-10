import 'package:flutter/material.dart';
import 'package:app1/core/themes/app_colors.dart';

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
  final bool isSimpleView;

  const FunctionMenuTile({
    super.key,
    required this.icon,
    required this.title,
    required this.bgColor,
    required this.onTap,
    this.isSimpleView = false,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    final borderColor = isDarkMode
        ? Colors.grey.shade700
        : Colors.grey.shade300;

    final iconBackgroundColor = isDarkMode
        ? AppColors.darkElevatedSurface
        : bgColor;

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
        border: Border.all(color: borderColor),
        borderRadius: BorderRadius.circular(20),
      ),
      child: ListTile(
        onTap: onTap,
        contentPadding: EdgeInsets.symmetric(
          horizontal: isSimpleView ? 18 : 15,
          vertical: isSimpleView ? 14 : 5,
        ),
        minVerticalPadding: isSimpleView ? 18 : 12,
        leading: Container(
          padding: EdgeInsets.all(isSimpleView ? 14 : 10),
          decoration: BoxDecoration(
            color: iconBackgroundColor,
            borderRadius: BorderRadius.circular(12),
          ),
          child: Icon(icon, color: iconColor, size: isSimpleView ? 34 : 24),
        ),
        title: Text(
          title,
          maxLines: 2,
          overflow: TextOverflow.ellipsis,
          style: TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: isSimpleView ? 19 : null,
            color: titleColor,
          ),
        ),
        trailing: Icon(
          Icons.chevron_right,
          color: trailingColor,
          size: isSimpleView ? 34 : 24,
        ),
      ),
    );
  }
}
