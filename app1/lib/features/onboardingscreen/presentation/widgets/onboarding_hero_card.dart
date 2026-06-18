import 'package:flutter/material.dart';
import '../../../authscreen/presentation/widgets/common/auth_buttons.dart';
import 'package:app1/core/config/app_assets.dart';
import 'package:app1/core/themes/app_colors.dart';
import 'careena_chat_bubble.dart';

/// Large onboarding card that presents the primary chat call to action.
class OnboardingHeroCard extends StatelessWidget {
  /// Called when the user wants to start chatting with Careena.
  final VoidCallback onPressed;

  const OnboardingHeroCard({super.key, required this.onPressed});

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        // The stacked illustration layout becomes too tight on compact screens,
        // so the body switches to a vertical arrangement below this width.
        final isCompact = constraints.maxWidth < 380;
        final horizontalMargin = isCompact ? 12.0 : 13.0;
        final isDarkMode = Theme.of(context).brightness == Brightness.dark;

        final cardColor = isDarkMode
            ? AppColors.darkElevatedSurface
            : Colors.white;

        return Padding(
          padding: EdgeInsets.symmetric(horizontal: horizontalMargin),
          child: Container(
            width: double.infinity,
            padding: EdgeInsets.all(isCompact ? 16 : 18),
            decoration: BoxDecoration(
              color: cardColor,
              borderRadius: BorderRadius.circular(20),

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
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  "Die richtige Hilfe,\nzum richtigen\nZeitpunkt.",
                  style: TextStyle(
                    fontSize: isCompact ? 24 : 28,
                    fontWeight: FontWeight.w800,
                    height: 1.2,
                    color: isDarkMode
                        ? Theme.of(context).colorScheme.onSurface
                        : AppColors.careenaTitle,
                  ),
                ),
                const SizedBox(height: 14),
                isCompact ? const _CompactHeroBody() : const _RegularHeroBody(),
                const SizedBox(height: 16),
                CareenaButton(
                  text: 'Jetzt mit Careena sprechen',
                  onPressed: onPressed,
                  backgroundColor: isDarkMode
                      ? AppColors.toolbarButtonBackgroundDark
                      : AppColors.careenaPrimary,
                  foregroundColor: isDarkMode
                      ? AppColors.toolbarButtonForegroundDark
                      : Colors.white,
                  borderRadius: 40,
                  height: 58,
                  side: BorderSide(color: AppColors.careenaGlow, width: 3),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}

/// Wide hero body that layers copy, speech bubble, and character artwork.
class _RegularHeroBody extends StatelessWidget {
  const _RegularHeroBody();

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 230,
      width: double.infinity,
      child: LayoutBuilder(
        builder: (context, constraints) {
          return Stack(
            children: [
              // Widths are proportional to the available card width so the
              // illustration stays balanced on tablet and desktop frames.
              Positioned(
                left: 0,
                top: 6,
                width: constraints.maxWidth * 0.58,
                child: const _HeroDescription(),
              ),
              Positioned(
                right: 0,
                top: 40,
                width: constraints.maxWidth * 0.44,
                child: const CareenaChatBubble(),
              ),
              Positioned(
                bottom: 0,
                left: constraints.maxWidth * 0.24,
                child: Image.asset(AppAssets.careenaHi, height: 140),
              ),
            ],
          );
        },
      ),
    );
  }
}

/// Narrow hero body that stacks the same content without overlapping.
class _CompactHeroBody extends StatelessWidget {
  const _CompactHeroBody();

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const _HeroDescription(),
        const SizedBox(height: 12),
        const Align(
          alignment: Alignment.centerRight,
          child: FractionallySizedBox(
            widthFactor: 0.78,
            child: CareenaChatBubble(),
          ),
        ),
        const SizedBox(height: 6),
        Center(child: Image.asset(AppAssets.careenaHi, height: 118)),
      ],
    );
  }
}

/// Short supporting copy below the main onboarding headline.
class _HeroDescription extends StatelessWidget {
  const _HeroDescription();

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Text(
      "Beschreibe deine Beschwerden\nund erhalte deine\npersönliche\nHandlungsempfehlung.",
      style: TextStyle(
        fontSize: 13,
        fontWeight: FontWeight.w500,
        color: isDarkMode ? colorScheme.onSurfaceVariant : Colors.black87,
        height: 1.3,
      ),
    );
  }
}
