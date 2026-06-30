import 'package:flutter/material.dart';
import 'package:app1/core/config/app_assets.dart';
import '../../../authscreen/presentation/widgets/common/auth_buttons.dart';
import 'package:app1/core/themes/app_colors.dart';
import 'careena_chat_bubble.dart';

const _heroTitle = "Die richtige Hilfe,\nzum richtigen\nZeitpunkt.";
const _heroTitleSemantic = "Die richtige Hilfe, zum richtigen Zeitpunkt.";
const _heroDescription =
    "Beschreibe deine Beschwerden\nund erhalte deine\npersönliche\nHandlungsempfehlung.";
const _heroDescriptionSemantic =
    "Beschreibe deine Beschwerden und erhalte deine persönliche Handlungsempfehlung.";
const _heroCtaLabel = 'Jetzt mit Careena sprechen';

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
            padding: EdgeInsets.all(
              useDenseLayout
                  ? 12
                  : (useCompactLayout ? 16 : (isCompact ? 16 : 18)),
            ),
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
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Semantics(
                  container: true,
                  header: true,
                  label: _heroTitleSemantic,
                  child: ExcludeSemantics(
                    child: Text(
                      _heroTitle,
                      style: TextStyle(
                        fontSize: useDenseLayout
                            ? 28
                            : (useCompactLayout ? 18 : (isCompact ? 24 : 32)),
                        fontWeight: FontWeight.w800,
                        height: useCompactLayout ? 1.16 : 1.2,
                        color: isDarkMode
                            ? Theme.of(context).colorScheme.onSurface
                            : AppColors.careenaTitle,
                      ),
                    ),
                  ),
                ),
                SizedBox(
                  height: useDenseLayout ? 8 : (useCompactLayout ? 8 : 14),
                ),
                if (useDenseLayout)
                  const _DenseHeroBody()
                else if (isCompact && !useCompactLayout)
                  const _CompactHeroBody()
                else
                  _RegularHeroBody(compact: useCompactLayout),
                SizedBox(
                  height: useDenseLayout ? 14 : (useCompactLayout ? 8 : 24),
                ),
                Align(
                  alignment: Alignment.center,
                  child: FractionallySizedBox(
                    widthFactor: useDenseLayout ? 0.92 : 1,
                    child: Semantics(
                      container: true,
                      button: true,
                      label: _heroCtaLabel,
                      onTap: onPressed,
                      child: ExcludeSemantics(
                        child: CareenaButton(
                          text: _heroCtaLabel,
                          onPressed: onPressed,
                          backgroundColor: isDarkMode
                              ? AppColors.toolbarButtonBackgroundDark
                              : AppColors.careenaPrimary,
                          foregroundColor: isDarkMode
                              ? AppColors.toolbarButtonForegroundDark
                              : AppColors.white,
                          borderRadius: 40,
                          height: useDenseLayout
                              ? 48
                              : (useCompactLayout ? 36 : 54),
                          fontSize: useDenseLayout
                              ? 16
                              : (useCompactLayout ? 14 : 18),
                          side: BorderSide(
                            color: AppColors.careenaGlow,
                            width: 3,
                          ),
                        ),
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
                right: 12,
                top: 4,
                child: Transform.scale(
                  scale: 1.18,
                  alignment: Alignment.topRight,
                  child: const _CareenaBubbleGroup(compact: true),
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
      height: compact ? 118 : 284,
      width: double.infinity,
      child: LayoutBuilder(
        builder: (context, constraints) {
          return Stack(
            clipBehavior: Clip.none,
            children: [
              // Widths are proportional to the available card width so the
              // illustration stays balanced on tablet and desktop frames.
              Positioned(
                left: 0,
                top: 6,
                width: constraints.maxWidth * (compact ? 0.46 : 0.58),
                child: compact
                    ? const _CompactWideHeroDescription()
                    : const _HeroDescription(),
              ),
              Positioned(
                right: compact ? 20 : 40,
                top: compact ? -34 : 34,
                child: _CareenaBubbleGroup(
                  compact: compact,
                  availableWidth: constraints.maxWidth,
                  compactWide: compact,
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}

class _CareenaBubbleGroup extends StatelessWidget {
  final bool compact;
  final bool compactWide;
  final double? availableWidth;

  const _CareenaBubbleGroup({
    required this.compact,
    this.compactWide = false,
    this.availableWidth,
  });

  @override
  Widget build(BuildContext context) {
    final width = availableWidth ?? 520;
    final scale = compact ? 0.0 : ((width - 400) / 220).clamp(0.0, 1.0);
    double mix(double small, double large) => small + (large - small) * scale;

    final groupWidth = compactWide ? 228.0 : (compact ? 210.0 : mix(200, 560));
    final groupHeight = compactWide ? 150.0 : (compact ? 142.0 : mix(142, 320));
    final bubbleWidth = compactWide ? 130.0 : (compact ? 112.0 : mix(132, 340));
    final bubbleLeft = compactWide ? 98.0 : (compact ? 98.0 : mix(66, 220));
    final careenaLeft = compactWide ? 24.0 : (compact ? 34.0 : mix(14, 73));
    final careenaTop = compactWide ? 38.0 : (compact ? 50.0 : mix(58, 122));
    final careenaHeight = compactWide ? 102.0 : (compact ? 98.0 : mix(76, 250));
    final bubbleFontSize = compactWide ? 7.3 : (compact ? 7.4 : mix(6.8, 15.5));
    final bubbleTop = compactWide ? -18.0 : (compact ? -18.0 : mix(0, 20));
    final bubbleText = scale > 0.66
        ? 'Ich bin Careena!\nDeine persönliche KI-Gesundheitsassistentin.'
        : scale > 0.25
        ? 'Ich bin Careena!\nDeine persönliche\nKI-Gesundheitsassistentin.'
        : 'Ich bin Careena!\nDeine persönliche\nKI-Gesundheits-\nassistentin.';

    return ExcludeSemantics(
      child: SizedBox(
        width: groupWidth,
        height: groupHeight,
        child: Stack(
          clipBehavior: Clip.none,
          children: [
            Positioned(
              left: bubbleLeft,
              top: bubbleTop,
              width: bubbleWidth,
              child: CareenaChatBubble(
                fontSize: bubbleFontSize,
                text: bubbleText,
              ),
            ),
            Positioned(
              left: careenaLeft,
              top: careenaTop,
              child: Image.asset(
                AppAssets.careenaHi,
                height: careenaHeight,
                excludeFromSemantics: true,
              ),
            ),
          ],
        ),
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
        const ExcludeSemantics(
          child: Align(
            alignment: Alignment.centerRight,
            child: FractionallySizedBox(
              widthFactor: 0.78,
              child: CareenaChatBubble(),
            ),
          ),
        ),
        const SizedBox(height: 6),
        ExcludeSemantics(
          child: Center(
            child: Image.asset(
              AppAssets.careenaHi,
              height: 118,
              excludeFromSemantics: true,
            ),
          ),
        ),
      ],
    );
  }
}

/// Smaller copy used in the compact wide hero to keep artwork and text apart.
class _CompactWideHeroDescription extends StatelessWidget {
  const _CompactWideHeroDescription();

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Semantics(
      label: _heroDescriptionSemantic,
      child: ExcludeSemantics(
        child: Text(
          _heroDescription,
          style: TextStyle(
            fontSize: 12.4,
            fontWeight: FontWeight.w500,
            color: isDarkMode
                ? colorScheme.onSurfaceVariant
                : AppColors.black87,
            height: 1.22,
          ),
        ),
      ),
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

    return Semantics(
      label: _heroDescriptionSemantic,
      child: ExcludeSemantics(
        child: Text(
          _heroDescription,
          style: TextStyle(
            fontSize: dense ? 12 : 14.5,
            fontWeight: FontWeight.w500,
            color: isDarkMode
                ? colorScheme.onSurfaceVariant
                : AppColors.black87,
            height: dense ? 1.24 : 1.3,
          ),
        ),
      ),
    );
  }
}
