import 'package:flutter/material.dart';
import '../../../../core/config/app_assets.dart';
import 'package:app1/core/themes/app_colors.dart';

class ChatAppBar extends StatelessWidget implements PreferredSizeWidget {
  final VoidCallback onBackPressed;

  const ChatAppBar({
    super.key,
    required this.onBackPressed,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkModeTheme = Theme.of(context).brightness == Brightness.dark;
    final avatarBackground = isDarkModeTheme
        ? AppColors.chatAvatarBackgroundDark
        : AppColors.chatAvatarBackgroundLight;

    return AppBar(
      leadingWidth: 72,
      elevation: 0,
      backgroundColor: colorScheme.surface,
      leading: IconButton(
        tooltip: 'Zurück',
        style: IconButton.styleFrom(
          backgroundColor: AppColors.toolbarButtonBackgroundDark,
          foregroundColor: AppColors.white,
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
                      color: AppColors.chatOnlineStatus,
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
    );
  }

  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);
}