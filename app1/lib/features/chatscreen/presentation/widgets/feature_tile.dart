import 'package:flutter/material.dart';
import '../themes/app_colors.dart';

/// Reusable clickable tile used by chat-related feature menus.
class FeatureTile extends StatelessWidget {
  /// Icon displayed in the tile avatar.
  final IconData icon;

  /// Tile label.
  final String title;

  /// Accent color for the icon and its soft background.
  final Color color;

  /// Optional tap callback; null leaves the tile visually static.
  final VoidCallback? onTap;

  const FeatureTile({
    super.key,
    required this.icon,
    required this.title,
    required this.color,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      cursor: SystemMouseCursors.click,
      child: GestureDetector(
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: AppColors.card,
            borderRadius: BorderRadius.circular(14),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.04),
                blurRadius: 6,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              CircleAvatar(
                radius: 18,
                backgroundColor: color.withValues(alpha: 0.1),
                child: Icon(icon, color: color),
              ),

              const SizedBox(height: 8),

              Text(
                title,
                textAlign: TextAlign.center,
                style: const TextStyle(fontWeight: FontWeight.w600),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
