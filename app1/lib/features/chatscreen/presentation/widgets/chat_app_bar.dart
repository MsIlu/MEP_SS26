import 'package:flutter/material.dart';
import '../../../../core/config/app_assets.dart';
import 'package:app1/core/themes/app_colors.dart';

class ChatAppBar extends StatelessWidget implements PreferredSizeWidget {
  final VoidCallback onBackPressed;
  final VoidCallback onToggleTheme;
  final bool isDarkMode;

  const ChatAppBar({
    super.key,
    required this.onBackPressed,
    required this.onToggleTheme,
    required this.isDarkMode,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkModeTheme = Theme.of(context).brightness == Brightness.dark;
    final avatarBackground = isDarkModeTheme
        ? const Color(0xFF86B2B2)
        : const Color(0xFFC3E7E7);

    return AppBar(
      leadingWidth: 72,
      elevation: 0,
      backgroundColor: colorScheme.surface,
      leading: IconButton(
        tooltip: 'Zurück',
        style: IconButton.styleFrom(
          backgroundColor: AppColors.toolbarButtonBackgroundDark,
          foregroundColor: Colors.white,
          fixedSize: const Size.square(44),
        ),
        onPressed: onBackPressed,
        icon: const Icon(Icons.west, size: 22),
      ),
      title: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          CircleAvatar(
            radius: 22,
            backgroundColor: avatarBackground,
            child: Padding(
              padding: const EdgeInsets.all(4),
              child: Image.asset(AppAssets.careenaProfil, fit: BoxFit.contain),
            ),
          ),
          const SizedBox(width: 15),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                "Careena",
                style: TextStyle(
                  color: colorScheme.onSurface,
                  fontWeight: FontWeight.bold,
                  fontSize: 18,
                ),
              ),
              Row(
                children: [
                  Container(
                    width: 7,
                    height: 7,
                    decoration: const BoxDecoration(
                      color: Colors.green,
                      shape: BoxShape.circle,
                    ),
                  ),
                  const SizedBox(width: 4),
                  Text(
                    "online",
                    style: TextStyle(
                      color: colorScheme.onSurfaceVariant,
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ],
      ),
      centerTitle: false,
      actions: [
        Padding(
          padding: const EdgeInsets.only(right: 12),

          child: IconButton(
            tooltip: isDarkMode
                ? 'Lightmode aktivieren'
                : 'Darkmode aktivieren',
            style: IconButton.styleFrom(
              backgroundColor: AppColors.toolbarButtonBackgroundDark,
              foregroundColor: Colors.white,
              fixedSize: const Size.square(44),
            ),
            icon: Icon(isDarkMode ? Icons.light_mode : Icons.dark_mode),
            onPressed: onToggleTheme,
          ),
        ),
      ],
    );
  }

  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);
}
