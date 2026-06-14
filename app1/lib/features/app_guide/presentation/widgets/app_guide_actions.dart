import 'package:flutter/material.dart';

import '../../../../core/themes/app_colors.dart';

class AppGuideActions extends StatelessWidget {
  final int currentStep;
  final int stepCount;
  final bool isLastStep;
  final VoidCallback? onPrevious;
  final VoidCallback onNext;
  final VoidCallback onSkip;

  const AppGuideActions({
    super.key,
    required this.currentStep,
    required this.stepCount,
    required this.isLastStep,
    required this.onPrevious,
    required this.onNext,
    required this.onSkip,
  });

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final isCompact = constraints.maxWidth < 360;

        return Column(
          children: [
            _GuideProgress(currentStep: currentStep, stepCount: stepCount),
            const SizedBox(height: 12),
            if (isCompact) ...[
              Row(
                children: [
                  _BackButton(onPressed: onPrevious),
                  const Spacer(),
                  _SkipButton(onPressed: onSkip, compact: true),
                ],
              ),
              const SizedBox(height: 8),
              SizedBox(
                width: double.infinity,
                child: _NextButton(isLastStep: isLastStep, onPressed: onNext),
              ),
            ] else
              Row(
                children: [
                  _BackButton(onPressed: onPrevious),
                  _SkipButton(onPressed: onSkip),
                  const Spacer(),
                  _NextButton(isLastStep: isLastStep, onPressed: onNext),
                ],
              ),
          ],
        );
      },
    );
  }
}

class _GuideProgress extends StatelessWidget {
  final int currentStep;
  final int stepCount;

  const _GuideProgress({required this.currentStep, required this.stepCount});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        for (var index = 0; index < stepCount; index++)
          Expanded(
            child: Container(
              height: 5,
              margin: EdgeInsets.only(right: index < stepCount - 1 ? 5 : 0),
              decoration: BoxDecoration(
                color: index <= currentStep
                    ? AppColors.careenaTeal
                    : AppColors.careenaBorder,
                borderRadius: BorderRadius.circular(5),
              ),
            ),
          ),
      ],
    );
  }
}

class _BackButton extends StatelessWidget {
  final VoidCallback? onPressed;

  const _BackButton({required this.onPressed});

  @override
  Widget build(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return IconButton(
      key: const ValueKey('app-guide-back-button'),
      tooltip: 'Vorheriger Schritt',
      onPressed: onPressed,
      style: IconButton.styleFrom(
        backgroundColor: isDarkMode
            ? AppColors.toolbarButtonBackgroundDark
            : AppColors.careenaDark,
        foregroundColor: isDarkMode
            ? AppColors.toolbarButtonForegroundDark
            : AppColors.toolbarButtonForeground,
        disabledBackgroundColor: isDarkMode
            ? AppColors.darkMutedSurface
            : AppColors.careenaBorder,
        disabledForegroundColor: isDarkMode
            ? AppColors.darkTextSecondary
            : AppColors.careenaMuted,
      ),
      icon: const Icon(Icons.arrow_back),
    );
  }
}

class _SkipButton extends StatelessWidget {
  final VoidCallback onPressed;
  final bool compact;

  const _SkipButton({required this.onPressed, this.compact = false});

  @override
  Widget build(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return TextButton(
      onPressed: onPressed,
      style: TextButton.styleFrom(
        foregroundColor: isDarkMode
            ? AppColors.toolbarButtonBackgroundDark
            : AppColors.careenaDark,
      ),
      child: Text(compact ? 'Beenden' : 'Tour beenden'),
    );
  }
}

class _NextButton extends StatelessWidget {
  final bool isLastStep;
  final VoidCallback onPressed;

  const _NextButton({required this.isLastStep, required this.onPressed});

  @override
  Widget build(BuildContext context) {
    return FilledButton.icon(
      key: const ValueKey('app-guide-next-button'),
      onPressed: onPressed,
      icon: Icon(isLastStep ? Icons.check : Icons.arrow_forward),
      label: Text(isLastStep ? 'Verstanden' : 'Weiter'),
      style: FilledButton.styleFrom(
        minimumSize: const Size(120, 48),
        backgroundColor: AppColors.careenaTeal,
        foregroundColor: AppColors.toolbarButtonForeground,
      ),
    );
  }
}
