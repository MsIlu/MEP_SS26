import 'package:flutter/material.dart';
import 'package:app1/core/themes/app_colors.dart';

/// Floating shortcut that returns the user to the newest chat message.
class LatestMessageButton extends StatelessWidget {
  /// Called when the button is pressed.
  final VoidCallback onPressed;

  const LatestMessageButton({super.key, required this.onPressed});

  @override
  Widget build(BuildContext context) {
    // Compact screens use an icon-only FAB so it does not cover too much of the
    // message list above the input field.
    final isCompact = MediaQuery.sizeOf(context).width < 380;

    return Semantics(
      button: true,
      label: 'Zur neuesten Nachricht springen',
      child: isCompact
          ? FloatingActionButton.small(
              heroTag: 'latest-message-button',
              onPressed: onPressed,
              elevation: 2,
              backgroundColor: AppColors.careenaBubbleBackground.withValues(
                alpha: 0.92,
              ),
              foregroundColor: AppColors.careenaDark,
              child: const Icon(Icons.keyboard_arrow_down),
            )
          : FloatingActionButton.extended(
              heroTag: 'latest-message-button',
              onPressed: onPressed,
              elevation: 2,
              backgroundColor: AppColors.careenaBubbleBackground.withValues(
                alpha: 0.92,
              ),
              foregroundColor: AppColors.careenaDark,
              icon: const Icon(Icons.keyboard_arrow_down),
              label: const Text('Zur neuesten Nachricht'),
            ),
    );
  }
}