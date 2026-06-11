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

    final borderColor = colorScheme.outlineVariant;

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

    final tileRadius = BorderRadius.circular(isSimpleView ? 28 : 20);

    return Material(
      color: colorScheme.surface,
      shape: RoundedRectangleBorder(
        borderRadius: tileRadius,
        side: BorderSide(color: borderColor),
      ),
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onTap,
        borderRadius: tileRadius,
        child: Padding(
          padding: EdgeInsets.symmetric(
            horizontal: isSimpleView ? 18 : 15,
            vertical: isSimpleView ? 16 : 10,
          ),
          child: Row(
            children: [
              _FeatureIconBadge(
                key: ValueKey('feature-icon-background-$title'),
                icon: icon,
                backgroundColor: iconBackgroundColor,
                foregroundColor: iconColor,
                isSimpleView: isSimpleView,
              ),
              SizedBox(width: isSimpleView ? 18 : 14),
              Expanded(
                child: Text(
                  title,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: isSimpleView ? 19 : null,
                    color: titleColor,
                  ),
                ),
              ),
              SizedBox(width: isSimpleView ? 12 : 8),
              Icon(
                Icons.chevron_right,
                color: trailingColor,
                size: isSimpleView ? 34 : 24,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _FeatureIconBadge extends StatelessWidget {
  final IconData icon;
  final Color backgroundColor;
  final Color foregroundColor;
  final bool isSimpleView;

  const _FeatureIconBadge({
    super.key,
    required this.icon,
    required this.backgroundColor,
    required this.foregroundColor,
    required this.isSimpleView,
  });

  @override
  Widget build(BuildContext context) {
    final size = isSimpleView ? 64.0 : 48.0;

    return SizedBox.square(
      dimension: size,
      child: DecoratedBox(
        decoration: BoxDecoration(
          color: backgroundColor,
          borderRadius: BorderRadius.circular(isSimpleView ? 18 : 12),
        ),
        child: Icon(icon, color: foregroundColor, size: isSimpleView ? 34 : 24),
      ),
    );
  }
}
