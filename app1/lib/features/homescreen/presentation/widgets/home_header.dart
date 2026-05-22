import 'package:flutter/material.dart';
import '../../../chatscreen/presentation/themes/app_colors.dart';

/// Legacy home header with optional overlapping avatar artwork.
class HomeHeader extends StatelessWidget {
  /// Optional avatar positioned partially outside the header container.
  final Widget? floatingAvatar;

  const HomeHeader({super.key, this.floatingAvatar});

  @override
  Widget build(BuildContext context) {
    return Stack(
      clipBehavior: Clip.none,
      children: [
        // Main header container
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [AppColors.primary, Color(0xFF6C63FF)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(20),
          ),
          child: Row(
            children: [
              // Placeholder space to avoid overlapping with floating avatar
              const SizedBox(width: 80),

              // Main header text section
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: const [
                    Text(
                      "Careena ist für dich da 🤍",
                      style: TextStyle(fontSize: 14, color: Colors.white70),
                    ),
                    SizedBox(height: 4),
                    Text(
                      "Wie kann ich dir helfen?",
                      style: TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                  ],
                ),
              ),

              // Notification icon on the right side
              const Icon(Icons.notifications_none, color: Colors.white),
            ],
          ),
        ),

        // Floating avatar positioned outside the card for a layered look.
        if (floatingAvatar != null)
          Positioned(
            left: -15,
            top: -32,
            child: Transform.translate(
              offset: const Offset(0, 20),
              child: SizedBox(height: 120, width: 120, child: floatingAvatar!),
            ),
          ),
      ],
    );
  }
}