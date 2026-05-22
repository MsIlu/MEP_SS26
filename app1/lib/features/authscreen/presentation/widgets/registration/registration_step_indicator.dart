import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../../../../chatscreen/presentation/themes/app_colors.dart';

/// Visual progress indicator for the registration flow.
class RegistrationStepIndicator extends StatelessWidget {
  final int currentStep;
  final ValueChanged<int>? onStepSelected;

  const RegistrationStepIndicator({
    super.key,
    required this.currentStep,
    this.onStepSelected,
  });

  @override
  Widget build(BuildContext context) {
    const labels = [
      'Persönliche\nDaten',
      'Gesundheits-\nangaben',
      'Überprüfung',
    ];

    return LayoutBuilder(
      builder: (context, constraints) {
        final stepWidth = _stepWidthFor(constraints.maxWidth);

        return Row(
          children: [
            for (var index = 0; index < labels.length; index++) ...[
              SizedBox(
                width: stepWidth,
                child: _StepItem(
                  index: index,
                  label: labels[index],
                  currentStep: currentStep,
                  onPressed: index < currentStep
                      ? () => onStepSelected?.call(index)
                      : null,
                ),
              ),
              if (index < labels.length - 1)
                Expanded(child: _StepConnector(isActive: index < currentStep)),
            ],
          ],
        );
      },
    );
  }

  double _stepWidthFor(double availableWidth) {
    if (availableWidth < 330) {
      return 82;
    }
    if (availableWidth < 390) {
      return 92;
    }
    return 108;
  }
}

class _StepConnector extends StatelessWidget {
  final bool isActive;

  const _StepConnector({required this.isActive});

  @override
  Widget build(BuildContext context) {
    return AnimatedContainer(
      duration: const Duration(milliseconds: 180),
      height: 4,
      margin: const EdgeInsets.only(left: 4, right: 4, bottom: 34),
      decoration: BoxDecoration(
        color: isActive ? AppColors.careenaPrimary : Colors.white,
        borderRadius: BorderRadius.circular(999),
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

    return Tooltip(
      message: isPastStep ? '$label bearbeiten' : label.replaceAll('\n', ' '),
      child: InkWell(
        borderRadius: BorderRadius.circular(14),
        onTap: onPressed,
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 4, horizontal: 2),
          child: Column(
            children: [
              AnimatedContainer(
                duration: const Duration(milliseconds: 180),
                width: 38,
                height: 38,
                decoration: BoxDecoration(
                  color: isActive ? AppColors.careenaPrimary : Colors.white,
                  shape: BoxShape.circle,
                  border: Border.all(color: AppColors.careenaPrimary),
                ),
                child: Center(
                  child: isPastStep
                      ? const Icon(Icons.check, color: Colors.white, size: 21)
                      : Text(
                          '${index + 1}',
                          style: TextStyle(
                            color: index == currentStep
                                ? Colors.white
                                : AppColors.careenaPrimary,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                ),
              ),
              const SizedBox(height: 6),
              Text(
                label,
                textAlign: TextAlign.center,
                style: GoogleFonts.nunito(
                  fontSize: 13,
                  height: 1.12,
                  fontWeight: FontWeight.w700,
                  color: AppColors.careenaTitle,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}