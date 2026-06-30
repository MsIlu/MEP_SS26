import 'package:app1/core/themes/app_colors.dart';
import 'package:app1/core/widgets/active_profile_header_action.dart';
import 'package:flutter/material.dart';

class CareenaPageHeader extends StatelessWidget implements PreferredSizeWidget {
  final String title;
  final bool showBack;
  final VoidCallback? onBack;
  final Widget? leading;
  final Widget? trailing;

  const CareenaPageHeader({
    super.key,
    required this.title,
    this.showBack = true,
    this.onBack,
    this.leading,
    this.trailing,
  });

  @override
  Size get preferredSize => const Size.fromHeight(64);

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final backgroundColor = isDark
        ? AppColors.headerBackgroundDark
        : AppColors.headerBackgroundLight;
    final trailingWidget = trailing ?? const ActiveProfileHeaderAction();
    final reservesWideTrailing =
        trailing != null || ActiveProfileHeaderAction.hasActiveProfile(context);
    final screenWidth = MediaQuery.sizeOf(context).width;
    final titleSidePadding = reservesWideTrailing
        ? (screenWidth >= 700 ? 228.0 : (screenWidth < 390 ? 112.0 : 156.0))
        : 64.0;

    return AppBar(
      automaticallyImplyLeading: false,
      elevation: 0,
      scrolledUnderElevation: 0,
      backgroundColor: backgroundColor,
      surfaceTintColor: backgroundColor,
      toolbarHeight: preferredSize.height,
      titleSpacing: 12,
      title: Stack(
        alignment: Alignment.center,
        children: [
          Align(
            alignment: Alignment.centerLeft,
            child:
                leading ??
                (showBack
                    ? CareenaHeaderAction(
                        tooltip: 'Zurück',
                        icon: Icons.arrow_back,
                        onPressed: onBack ?? () => Navigator.maybePop(context),
                      )
                    : const SizedBox.square(dimension: 48)),
          ),
          Padding(
            padding: EdgeInsets.symmetric(horizontal: titleSidePadding),
            child: Tooltip(
              message: title,
              child: Text(
                title,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: Theme.of(context).colorScheme.onSurface,
                  fontSize: 20,
                  fontWeight: FontWeight.w800,
                ),
              ),
            ),
          ),
          Align(alignment: Alignment.centerRight, child: trailingWidget),
        ],
      ),
    );
  }
}

class CareenaHeaderAction extends StatelessWidget {
  final String tooltip;
  final IconData icon;
  final VoidCallback? onPressed;

  const CareenaHeaderAction({
    super.key,
    required this.tooltip,
    required this.icon,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return IconButton(
      tooltip: tooltip,
      style: IconButton.styleFrom(
        backgroundColor: isDark
            ? AppColors.toolbarButtonBackgroundDark
            : AppColors.toolbarButtonBackground,
        foregroundColor: isDark
            ? AppColors.toolbarButtonForegroundDark
            : AppColors.toolbarButtonForeground,
        fixedSize: const Size.square(48),
      ),
      onPressed: onPressed,
      icon: Icon(icon),
    );
  }
}
