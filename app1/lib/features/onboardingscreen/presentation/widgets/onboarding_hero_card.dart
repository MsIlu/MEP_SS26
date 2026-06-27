import 'package:flutter/material.dart';
import 'package:app1/core/config/app_assets.dart';
import '../../../authscreen/presentation/widgets/common/auth_buttons.dart';
import 'package:app1/core/themes/app_colors.dart';
import 'careena_chat_bubble.dart';

const _heroTitle = "Die richtige Hilfe,\nzum richtigen\nZeitpunkt.";
const _heroDescription =
    "Beschreibe deine Beschwerden\nund erhalte deine\npersönliche\nHandlungsempfehlung.";

/// Large onboarding card that presents the primary chat call to action.
class OnboardingHeroCard extends StatelessWidget {
  /// Called when the user wants to start chatting with Careena.
  final VoidCallback onPressed;
  final bool dense;
  final bool compact;

  const OnboardingHeroCard({
    super.key,
    required this.onPressed,
    this.dense = false,
    this.compact = false,
  });

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        // The stacked illustration layout becomes too tight on compact screens,
        // so the body switches to a vertical arrangement below this width.
        final isCompact = constraints.maxWidth < 380;
        final useDenseLayout = dense || constraints.maxHeight < 390;
        final useCompactLayout = compact && !useDenseLayout;
        final horizontalMargin = isCompact || useDenseLayout ? 10.0 : 13.0;
        final isDarkMode = Theme.of(context).brightness == Brightness.dark;

        final cardColor = isDarkMode
            ? AppColors.darkElevatedSurface
            : AppColors.white;

        return Padding(
          padding: EdgeInsets.symmetric(horizontal: horizontalMargin),
          child: Container(
            width: double.infinity,
            padding: EdgeInsets.all(useDenseLayout ? 12 : (isCompact ? 16 : 18)),
            decoration: BoxDecoration(
              color: cardColor,
              borderRadius: BorderRadius.circular(20),

              border: Border.all(
                color: AppColors.careenaGlow,
                width: 2,
              ),
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
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  _heroTitle,
                  style: TextStyle(
                    fontSize: useDenseLayout ? 28 : (isCompact ? 24 : 28),
                    fontWeight: FontWeight.w800,
                    height: 1.2,
                    color: isDarkMode
                        ? Theme.of(context).colorScheme.onSurface
                        : AppColors.careenaTitle,
                  ),
                ),
                SizedBox(height: useDenseLayout ? 8 : 14),
                if (useDenseLayout)
                  const _DenseHeroBody()
                else if (isCompact)
                  const _CompactHeroBody()
                else
                  _RegularHeroBody(compact: useCompactLayout),
                SizedBox(height: useDenseLayout ? 10 : 16),
                Align(
                  alignment: Alignment.center,
                  child: FractionallySizedBox(
                    widthFactor: useDenseLayout ? 0.92 : 1,
                    child: CareenaButton(
                      text: 'Jetzt mit Careena sprechen',
                      onPressed: onPressed,
                      backgroundColor: isDarkMode
                          ? AppColors.toolbarButtonBackgroundDark
                          : AppColors.careenaPrimary,
                      foregroundColor: isDarkMode
                          ? AppColors.toolbarButtonForegroundDark
                          : AppColors.white,
                      borderRadius: 40,
                      height: useDenseLayout ? 48 : (useCompactLayout ? 46 : 58),
                      fontSize: useDenseLayout ? 16 : 18,
                      side: BorderSide(
                        color: AppColors.careenaGlow,
                        width: 3,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}

/// Condensed hero body for short screens where the auth buttons must remain visible.
class _DenseHeroBody extends StatelessWidget {
  const _DenseHeroBody();

  @override
  Widget build(BuildContext context) {
    const bubbleRight = -54.0;
    const bubbleTop = 14.0;
    const bubbleWidth = 140.0;
    const careenaLeft = 20.0;
    const careenaTop = 74.0;
    const careenaHeight = 116.0;

    return SizedBox(
      height: 178,
      width: double.infinity,
      child: LayoutBuilder(
        builder: (context, constraints) {
          final illustrationWidth = (constraints.maxWidth * 0.52).clamp(
            188.0,
            216.0,
          );

          return Stack(
            clipBehavior: Clip.none,
            children: [
              Positioned(
                left: 0,
                top: 0,
                width: constraints.maxWidth - illustrationWidth + 10,
                child: const _HeroDescription(dense: true),
              ),
              Positioned(
                right: 64,
                top: -16,
                width: illustrationWidth,
                height: 190,
                child: Stack(
                  clipBehavior: Clip.none,
                  children: [
                    const Positioned(
                      right: bubbleRight,
                      top: bubbleTop,
                      width: bubbleWidth,
                      child: CareenaChatBubble(fontSize: 10),
                    ),
                    Positioned(
                      left: careenaLeft,
                      top: careenaTop,
                      child: Image.asset(
                        AppAssets.careenaHi,
                        height: careenaHeight,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}

/// Wide hero body that layers copy, speech bubble, and character artwork.
class _RegularHeroBody extends StatelessWidget {
  final bool compact;

  const _RegularHeroBody({this.compact = false});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: compact ? 160 : 190,
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
                right: 34,
                top: compact ? 28 : 36,
                width: constraints.maxWidth * 0.36,
                child: CareenaChatBubble(fontSize: compact ? 9 : 10),
              ),
              Positioned(
                bottom: compact ? 0 : 4,
                left: constraints.maxWidth * 0.33,
                child: Image.asset(
                  AppAssets.careenaHi,
                  height: compact ? 92 : 108,
                ),
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
  final bool dense;

  const _HeroDescription({this.dense = false});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Text(
      _heroDescription,
      style: TextStyle(
        fontSize: dense ? 12 : 13,
        fontWeight: FontWeight.w500,
        color: isDarkMode ? colorScheme.onSurfaceVariant : AppColors.black87,
        height: dense ? 1.24 : 1.3,
      ),
    );
  }
}
