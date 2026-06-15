import 'package:flutter/material.dart';

import '../../../../core/config/app_assets.dart';
import '../../../homescreen/presentation/widgets/floating_avatar.dart';
import '../../../onboardingscreen/presentation/widgets/careena_chat_bubble.dart';
import '../../data/app_guide_steps.dart';
import 'app_guide_actions.dart';

class AppGuideCompanion extends StatelessWidget {
  final AppGuideStep step;
  final int currentStep;
  final int stepCount;
  final VoidCallback? onPrevious;
  final VoidCallback onNext;
  final VoidCallback onSkip;

  const AppGuideCompanion({
    super.key,
    required this.step,
    required this.currentStep,
    required this.stepCount,
    required this.onPrevious,
    required this.onNext,
    required this.onSkip,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 600),
        child: LayoutBuilder(
          builder: (context, constraints) {
            final isCompact = constraints.maxWidth < 430;
            final avatar = FloatingAvatar(
              imagePath: AppAssets.careenaHi,
              size: isCompact ? 68 : 82,
              showFrame: false,
            );
            final bubble = CareenaChatBubble(
              title: step.title,
              text: step.description,
              fontSize: isCompact ? 15 : 16,
              useDarkSurfaceInDarkMode: true,
              footer: AppGuideActions(
                currentStep: currentStep,
                stepCount: stepCount,
                isLastStep: currentStep == stepCount - 1,
                onPrevious: onPrevious,
                onNext: onNext,
                onSkip: onSkip,
              ),
            );

            if (isCompact) {
              return Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Padding(
                    padding: const EdgeInsets.only(left: 8, bottom: 4),
                    child: avatar,
                  ),
                  bubble,
                ],
              );
            }

            return Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                avatar,
                const SizedBox(width: 6),
                Expanded(child: bubble),
              ],
            );
          },
        ),
      ),
    );
  }
}
