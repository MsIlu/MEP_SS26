import 'package:flutter/material.dart';

import '../../../../core/themes/app_colors.dart';
import '../../data/app_guide_steps.dart';
import 'app_guide_companion.dart';
import 'app_guide_spotlight_painter.dart';

class AppGuideOverlay extends StatelessWidget {
  final GlobalKey targetKey;
  final AppGuideStep step;
  final int currentStep;
  final int stepCount;
  final VoidCallback? onPrevious;
  final VoidCallback onNext;
  final VoidCallback onSkip;

  const AppGuideOverlay({
    super.key,
    required this.targetKey,
    required this.step,
    required this.currentStep,
    required this.stepCount,
    required this.onPrevious,
    required this.onNext,
    required this.onSkip,
  });

  @override
  Widget build(BuildContext context) {
    final targetBox =
        targetKey.currentContext?.findRenderObject() as RenderBox?;
    if (targetBox == null || !targetBox.hasSize) return const SizedBox.shrink();
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Semantics(
      scopesRoute: true,
      explicitChildNodes: true,
      label: 'App-Tour, Schritt ${currentStep + 1} von $stepCount',
      child: Material(
        type: MaterialType.transparency,
        child: LayoutBuilder(
          builder: (context, constraints) {
            final targetRect = _targetRectInOverlay(targetBox, context);
            final spotlight = _spotlightRect(targetRect, constraints.biggest);
            final showMessageAbove =
                spotlight.center.dy > constraints.maxHeight / 2;
            final safePadding = MediaQuery.paddingOf(context);

            return Stack(
              children: [
                Positioned.fill(
                  child: GestureDetector(
                    behavior: HitTestBehavior.opaque,
                    onTap: () {},
                    child: CustomPaint(
                      key: const ValueKey('app-guide-white-scrim'),
                      painter: AppGuideSpotlightPainter(
                        spotlight: spotlight,
                        radius: step.spotlightRadius,
                        scrimColor: isDarkMode
                            ? AppColors.darkBackground.withValues(alpha: 0.88)
                            : AppColors.lightBackground.withValues(alpha: 0.84),
                        outlineColor: isDarkMode
                            ? AppColors.toolbarButtonBackgroundDark
                            : AppColors.careenaTeal,
                      ),
                    ),
                  ),
                ),
                Positioned(
                  left: 12,
                  right: 12,
                  top: showMessageAbove ? safePadding.top + 12 : null,
                  bottom: showMessageAbove ? null : safePadding.bottom + 12,
                  child: AppGuideCompanion(
                    step: step,
                    currentStep: currentStep,
                    stepCount: stepCount,
                    onPrevious: onPrevious,
                    onNext: onNext,
                    onSkip: onSkip,
                  ),
                ),
              ],
            );
          },
        ),
      ),
    );
  }

  Rect _targetRectInOverlay(RenderBox targetBox, BuildContext overlayContext) {
    final overlayBox = overlayContext.findRenderObject() as RenderBox?;
    if (overlayBox == null || !overlayBox.hasSize) {
      return targetBox.localToGlobal(Offset.zero) & targetBox.size;
    }

    final targetTopLeft = overlayBox.globalToLocal(
      targetBox.localToGlobal(Offset.zero),
    );
    final targetBottomRight = overlayBox.globalToLocal(
      targetBox.localToGlobal(targetBox.size.bottomRight(Offset.zero)),
    );
    return Rect.fromPoints(targetTopLeft, targetBottomRight);
  }

  Rect _spotlightRect(Rect target, Size screenSize) {
    const padding = 3.0;
    return Rect.fromLTRB(
      (target.left - padding).clamp(4, screenSize.width - 4),
      (target.top - padding).clamp(4, screenSize.height - 4),
      (target.right + padding).clamp(4, screenSize.width - 4),
      (target.bottom + padding).clamp(4, screenSize.height - 4),
    );
  }
}