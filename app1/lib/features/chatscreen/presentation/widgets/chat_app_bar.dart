import 'package:flutter/material.dart';
import '../../../../core/config/app_assets.dart';
import '../themes/app_colors.dart';

/// App bar for the chat screen with Careena identity and status.
class ChatAppBar extends StatelessWidget implements PreferredSizeWidget {
  final VoidCallback onBackPressed;

  const ChatAppBar({
    super.key,
    required this.onBackPressed,
  });

  @override
  Widget build(BuildContext context) {
    return AppBar(
      elevation: 0,
      backgroundColor: Colors.white,
      leading: IconButton(
        icon: const Icon(
          Icons.chevron_left,
          color: AppColors.careenaDark,
          size: 30,
        ),
        onPressed: onBackPressed,
      ),
      title: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Avatar that visually connects the app bar to assistant messages.
          const CircleAvatar(
            radius: 18,
            backgroundColor: AppColors.careenaBubbleBackground,
            backgroundImage: AssetImage(AppAssets.careenaDoctor),
          ),
          const SizedBox(width: 10),
          // Name and simple status indicator for the assistant persona.
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                "Careena",
                style: TextStyle(
                  color: AppColors.careenaDark,
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
                  const Text(
                    "online",
                    style: TextStyle(color: Colors.grey, fontSize: 12),
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