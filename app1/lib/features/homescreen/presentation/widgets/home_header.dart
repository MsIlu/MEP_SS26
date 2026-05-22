import 'package:flutter/material.dart';

import '../../../chatscreen/presentation/themes/app_colors.dart';
import 'notification_badge_icon.dart';

/// Top row with greeting text and notification badge for the home screen.
class HomeHeader extends StatelessWidget {
  /// Whether the header should use the narrow phone spacing.
  final bool isCompact;

  const HomeHeader({super.key, required this.isCompact});

  @override
  Widget build(BuildContext context) {
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
                color: AppColors.careenaDark,
              ),
            ),
          ),
          const SizedBox(width: 12),
          const NotificationBadgeIcon(count: 3),
        ],
      ),
    );
  }
}