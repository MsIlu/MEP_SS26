import 'package:flutter/material.dart';

/// Notification icon with a small numeric badge.
class NotificationBadgeIcon extends StatelessWidget {
  /// Number displayed in the badge; zero hides the badge entirely.
  final int count;

  const NotificationBadgeIcon({super.key, required this.count});

  @override
  Widget build(BuildContext context) {
    return Stack(
      clipBehavior: Clip.none,
      children: [
        const Icon(
          Icons.notifications_none,
          size: 30,
          color: Color(0xFF8BB5BC),
        ),
        if (count > 0)
          Positioned(
            right: 0,
            child: CircleAvatar(
              radius: 7,
              backgroundColor: Colors.red,
              child: Text(
                count.toString(),
                style: const TextStyle(color: Colors.white, fontSize: 8),
              ),
            ),
          ),
      ],
    );
  }
}