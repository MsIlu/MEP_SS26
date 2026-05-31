import 'package:flutter/material.dart';
import '../../../chatscreen/presentation/themes/app_colors.dart';
import 'notification_badge_icon.dart';

/// Top row with greeting text and notification badge for the home screen.
class HomeHeader extends StatelessWidget {
  /// Whether the header should use the narrow phone spacing.
  final bool isCompact;
  final VoidCallback onToggleTheme;
  final bool isDarkMode;

  const HomeHeader({
    super.key,
    required this.isCompact,
    required this.onToggleTheme,
    required this.isDarkMode,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkTheme = Theme.of(context).brightness == Brightness.dark;

    return Padding(
      padding: EdgeInsets.fromLTRB(
        isCompact ? 16 : 20,
        20,
        isCompact ? 16 : 20,
        10,
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Expanded(
            child: Text(
              'Willkommen!',
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: TextStyle(
                fontSize: isCompact ? 24 : 28,
                fontWeight: FontWeight.bold,
                color: colorScheme.onSurface,
              ),
            ),
          ),
          const SizedBox(width: 12),
          IconButton(
            tooltip: isDarkMode ? 'Lightmode aktivieren' : 'Darkmode aktivieren',
            style: IconButton.styleFrom(
              backgroundColor: isDarkTheme
                  ? AppColors.toolbarButtonBackgroundDark
                  : AppColors.toolbarButtonBackground,
              foregroundColor: isDarkTheme
                  ? AppColors.toolbarButtonForegroundDark
                  : AppColors.toolbarButtonForeground,
            ),
            icon: Icon(isDarkMode ? Icons.light_mode : Icons.dark_mode),
            onPressed: onToggleTheme,
          ),
          const SizedBox(width: 8),
          const NotificationBadgeIcon(count: 3),
        ],
      ),
    );
  }
}