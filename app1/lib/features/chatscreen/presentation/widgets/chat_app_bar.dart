import 'package:flutter/material.dart';
import '../../../../core/config/app_assets.dart';

/// App bar for the chat screen with Careena identity and status.
class ChatAppBar extends StatelessWidget implements PreferredSizeWidget {
  final VoidCallback onToggleTheme;
  final bool isDarkMode;

  const ChatAppBar({
    super.key,
    required this.onToggleTheme,
    required this.isDarkMode,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return AppBar(
      elevation: 0,
      backgroundColor: colorScheme.surface,
      leading: IconButton(
        icon: Icon(
          Icons.chevron_left,
          color: colorScheme.onSurface,
          size: 30,
        ),
        onPressed: () => Navigator.pop(context),
      ),
      title: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Avatar that visually connects the app bar to assistant messages.
          CircleAvatar(
            radius: 18,
            backgroundColor: colorScheme.surfaceContainerHighest,
            backgroundImage: const AssetImage(AppAssets.careenaDoctor),
          ),
          const SizedBox(width: 10),
          // Name and simple status indicator for the assistant persona.
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
        IconButton(
          tooltip: isDarkMode ? 'Lightmode aktivieren' : 'Darkmode aktivieren',
          icon: Icon(
            isDarkMode ? Icons.light_mode : Icons.dark_mode,
            color: colorScheme.onSurface,
          ),
          onPressed: onToggleTheme,
        ),
      ],
    );
  }

  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);
}
