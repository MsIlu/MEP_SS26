import 'package:flutter/material.dart';
import '../../../../core/config/app_assets.dart';
import '../../../authscreen/presentation/widgets/common/auth_buttons.dart';
import 'package:app1/core/themes/app_colors.dart';
import 'floating_avatar.dart';

/// Home-screen card that invites the user into a Careena chat.
class CareenaHeroCard extends StatelessWidget {
  /// Called when the user taps the hero action.
  final VoidCallback onTap;
  final bool isSimpleView;

  const CareenaHeroCard({
    super.key,
    required this.onTap,
    this.isSimpleView = false,
  });

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        // Switch from side-by-side to stacked layout before the avatar and text
        // start competing for horizontal space.
        final isCompact = constraints.maxWidth < 360;
        final avatarSize = isCompact ? 78.0 : 100.0;
        final isDarkMode = Theme.of(context).brightness == Brightness.dark;

        final cardColor = isDarkMode
            ? AppColors.darkElevatedSurface
            : AppColors.careenaInfoBorder;

        return Container(
          margin: EdgeInsets.symmetric(
            horizontal: isCompact ? 14 : 20,
            vertical: 10,
          ),
          padding: EdgeInsets.all(isCompact ? 16 : 20),
          decoration: BoxDecoration(
            color: cardColor,
            borderRadius: BorderRadius.circular(30),
            border: Border.all(color: AppColors.careenaGlow, width: 2),
            boxShadow: [
              BoxShadow(
                color: AppColors.careenaGlow.withValues(
                  alpha: isDarkMode ? 0.15 : 0.08,
                ),
                blurRadius: isDarkMode ? 12 : 8,
                spreadRadius: 1,
              ),
            ],
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
                    _HeroTextAndAction(
                      onTap: onTap,
                      isSimpleView: isSimpleView,
                    ),
                  ],
                )
              : Row(
                  children: [
                    FloatingAvatar(
                      imagePath: AppAssets.careenaDoctor,
                      size: avatarSize,
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: _HeroTextAndAction(
                        onTap: onTap,
                        isSimpleView: isSimpleView,
                      ),
                    ),
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
  final bool isSimpleView;

  const _HeroTextAndAction({required this.onTap, required this.isSimpleView});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    final titleColor = isDarkMode
        ? colorScheme.onSurface
        : AppColors.careenaDark;

    final buttonColor = isDarkMode
        ? AppColors.toolbarButtonBackgroundDark
        : AppColors.careenaTeal;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          "Ich bin Careena!\nWie kann ich dir helfen?",
          style: TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: isSimpleView ? 20 : 16,
            color: titleColor,
          ),
        ),
        const SizedBox(height: 11),
        CareenaButton(
          text: 'Jetzt mit Careena sprechen',
          onPressed: onTap,
          backgroundColor: buttonColor,
          foregroundColor: isDarkMode
              ? AppColors.toolbarButtonForegroundDark
              : AppColors.toolbarButtonForeground,
          borderRadius: isSimpleView ? 26 : 20,
          height: isSimpleView ? 64 : 44,
          fontSize: isSimpleView ? 17 : 13,

          side: BorderSide(color: AppColors.careenaGlow, width: 4),
        ),
      ],
    );
  }
}