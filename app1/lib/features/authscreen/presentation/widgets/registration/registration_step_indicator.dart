import 'package:flutter/material.dart';
import 'package:app1/core/themes/app_colors.dart';

const _circleSize = 42.0;
const _connectorHeight = 4.0;

/// Visual progress indicator for the registration flow.
class RegistrationStepIndicator extends StatelessWidget {
  final int currentStep;
  final List<String> labels;
  final ValueChanged<int>? onStepSelected;

  const RegistrationStepIndicator({
    super.key,
    required this.currentStep,
    this.labels = const [
      'Persönliche\nDaten',
      'Gesundheits-\nangaben',
      'Überprüfung',
    ],
    this.onStepSelected,
  });

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        Positioned(
          top: (_circleSize - _connectorHeight) / 2,
          left: 0,
          right: 0,
          child: Row(
            children: [
              const Expanded(child: SizedBox()),
              for (var index = 0; index < labels.length - 1; index++)
                Expanded(
                  flex: 2,
                  child: _StepConnector(
                    key: ValueKey('registration-step-connector-$index'),
                    isActive: index < currentStep,
                  ),
                ),
              const Expanded(child: SizedBox()),
            ],
          ),
        ),
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            for (var index = 0; index < labels.length; index++)
              Expanded(
                child: _StepItem(
                  index: index,
                  label: labels[index],
                  currentStep: currentStep,
                  onPressed: index < currentStep
                      ? () => onStepSelected?.call(index)
                      : null,
                ),
              ),
          ],
        ),
      ],
    );
  }
}

class _StepConnector extends StatelessWidget {
  final bool isActive;

  const _StepConnector({super.key, required this.isActive});

  @override
  Widget build(BuildContext context) {
    final color = isActive
        ? AppColors.careenaPrimary
        : AppColors.careenaPrimary.withValues(alpha: 0.32);

    return AnimatedContainer(
      duration: const Duration(milliseconds: 180),
      height: _connectorHeight,
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(_connectorHeight),
      ),
    );
  }
}

class _StepItem extends StatelessWidget {
  final int index;
  final String label;
  final int currentStep;
  final VoidCallback? onPressed;

  const _StepItem({
    required this.index,
    required this.label,
    required this.currentStep,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    final isActive = index <= currentStep;
    final isPastStep = index < currentStep;
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Tooltip(
      message: isPastStep ? '$label bearbeiten' : label.replaceAll('\n', ' '),
      child: InkWell(
        borderRadius: BorderRadius.circular(14),
        onTap: onPressed,
        child: Column(
          children: [
            AnimatedContainer(
              key: ValueKey('registration-step-circle-$index'),
              duration: const Duration(milliseconds: 180),
              width: _circleSize,
              height: _circleSize,
              decoration: BoxDecoration(
                color: isActive
                    ? AppColors.careenaPrimary
                    : Theme.of(context).colorScheme.surface,
                shape: BoxShape.circle,
                border: Border.all(color: AppColors.careenaPrimary, width: 2),
              ),
              child: Center(
                child: isPastStep
                    ? const Icon(
                        Icons.check,
                        color: AppColors.toolbarButtonForeground,
                        size: 23,
                      )
                    : Text(
                        '${index + 1}',
                        style: TextStyle(
                          color: index == currentStep
                              ? AppColors.toolbarButtonForeground
                              : AppColors.careenaPrimary,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
              ),
            ),
            const SizedBox(height: 8),
            Text(
              label,
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 13,
                height: 1.12,
                fontWeight: FontWeight.w700,
                color: isDarkMode
                    ? colorScheme.onSurface
                    : AppColors.careenaTitle,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
