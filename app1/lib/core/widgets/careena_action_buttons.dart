import 'package:app1/core/themes/app_colors.dart';
import 'package:flutter/material.dart';

/// Shared icon button for compact Careena actions such as add and close.
class CareenaIconActionButton extends StatelessWidget {
  final String tooltip;
  final IconData icon;
  final VoidCallback? onPressed;
  final Color? backgroundColor;
  final Color? foregroundColor;
  final Size size;

  const CareenaIconActionButton({
    super.key,
    required this.tooltip,
    required this.icon,
    required this.onPressed,
    this.backgroundColor,
    this.foregroundColor,
    this.size = const Size(48, 48),
  });

  const CareenaIconActionButton.add({
    super.key,
    required this.tooltip,
    required this.onPressed,
    this.size = const Size(48, 48),
  }) : icon = Icons.add,
       backgroundColor = AppColors.toolbarButtonBackground,
       foregroundColor = AppColors.toolbarButtonForeground;

  const CareenaIconActionButton.close({
    super.key,
    this.tooltip = 'Abbrechen',
    required this.onPressed,
    this.size = const Size(40, 40),
  }) : icon = Icons.close,
       backgroundColor = null,
       foregroundColor = null;

  @override
  Widget build(BuildContext context) {
    if (backgroundColor == null && foregroundColor == null) {
      return IconButton(
        tooltip: tooltip,
        onPressed: onPressed,
        icon: Icon(icon),
      );
    }

    return IconButton.filled(
      tooltip: tooltip,
      style: IconButton.styleFrom(
        backgroundColor: backgroundColor,
        foregroundColor: foregroundColor,
        fixedSize: size,
      ),
      onPressed: onPressed,
      icon: Icon(icon),
    );
  }
}

/// Shared filled command button for form submissions.
class CareenaPrimaryIconButton extends StatelessWidget {
  final String label;
  final IconData icon;
  final VoidCallback? onPressed;

  const CareenaPrimaryIconButton({
    super.key,
    required this.label,
    required this.icon,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return FilledButton.icon(
      onPressed: onPressed,
      icon: Icon(icon),
      label: Text(label),
      style: FilledButton.styleFrom(
        backgroundColor: AppColors.toolbarButtonBackground,
        foregroundColor: AppColors.toolbarButtonForeground,
        padding: const EdgeInsets.symmetric(vertical: 14),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      ),
    );
  }
}

/// Shared two-button navigation for short step-based forms.
class CareenaStepNavigation extends StatelessWidget {
  final String backLabel;
  final String nextLabel;
  final IconData backIcon;
  final IconData nextIcon;
  final bool isBusy;
  final VoidCallback? onBack;
  final VoidCallback onNext;

  const CareenaStepNavigation({
    super.key,
    required this.backLabel,
    required this.nextLabel,
    required this.backIcon,
    required this.nextIcon,
    required this.isBusy,
    required this.onBack,
    required this.onNext,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: OutlinedButton.icon(
            onPressed: onBack,
            icon: Icon(backIcon),
            label: Text(backLabel),
            style: OutlinedButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 14),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
            ),
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: CareenaPrimaryIconButton(
            onPressed: isBusy ? null : onNext,
            icon: nextIcon,
            label: nextLabel,
          ),
        ),
      ],
    );
  }
}
