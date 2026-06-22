import 'package:flutter/material.dart';

import '../themes/app_colors.dart';

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
            padding: const EdgeInsets.symmetric(horizontal: 64),
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
          Align(
            alignment: Alignment.centerRight,
            child: trailing ?? const SizedBox.square(dimension: 48),
          ),
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

class CareenaThemeHeaderAction extends StatelessWidget {
  final VoidCallback onPressed;
  final bool isDarkMode;

  const CareenaThemeHeaderAction({
    super.key,
    required this.onPressed,
    required this.isDarkMode,
  });

  @override
  Widget build(BuildContext context) {
    return CareenaHeaderAction(
      tooltip: isDarkMode ? 'Lightmode aktivieren' : 'Darkmode aktivieren',
      icon: isDarkMode ? Icons.light_mode : Icons.dark_mode,
      onPressed: onPressed,
    );
  }
}
