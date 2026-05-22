import 'package:flutter/material.dart';
import '../../../../core/config/app_assets.dart';
import 'floating_avatar.dart';

/// Home-screen card that invites the user into a Careena chat.
class CareenaHeroCard extends StatelessWidget {
  /// Called when the user taps the hero action.
  final VoidCallback onTap;
  const CareenaHeroCard({super.key, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        // Switch from side-by-side to stacked layout before the avatar and text
        // start competing for horizontal space.
        final isCompact = constraints.maxWidth < 360;
        final avatarSize = isCompact ? 78.0 : 100.0;

        return Container(
          margin: EdgeInsets.symmetric(
            horizontal: isCompact ? 14 : 20,
            vertical: 10,
          ),
          padding: EdgeInsets.all(isCompact ? 16 : 20),
          decoration: BoxDecoration(
            color: const Color(0xFFB8E4E8),
            borderRadius: BorderRadius.circular(30),
          ),
          child: isCompact
              ? Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Center(
                      child: FloatingAvatar(
                        imagePath: AppAssets.careenaDoctor,
                        size: avatarSize,
                      ),
                    ),
                    const SizedBox(height: 14),
                    _HeroTextAndAction(onTap: onTap),
                  ],
                )
              : Row(
                  children: [
                    FloatingAvatar(
                      imagePath: AppAssets.careenaDoctor,
                      size: avatarSize,
                    ),
                    const SizedBox(width: 16),
                    Expanded(child: _HeroTextAndAction(onTap: onTap)),
                  ],
                ),
        );
      },
    );
  }
}

/// Text and call-to-action section shared by compact and regular hero layouts.
class _HeroTextAndAction extends StatelessWidget {
  /// Opens the chat screen.
  final VoidCallback onTap;

  const _HeroTextAndAction({required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          "Ich bin Careena!\nWie kann ich dir helfen?",
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
        ),
        const SizedBox(height: 11),
        ElevatedButton(
          onPressed: onTap,
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFF26A69A),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(20),
            ),
          ),
          child: const FittedBox(
            fit: BoxFit.scaleDown,
            child: Text(
              "Jetzt mit Careena sprechen",
              style: TextStyle(color: Colors.white, fontSize: 13),
            ),
          ),
        ),
      ],
    );
  }
}