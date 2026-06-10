import 'package:flutter/material.dart';
import '../themes/app_colors.dart';

class LatestMessageButton extends StatelessWidget {
  final VoidCallback onPressed;

  const LatestMessageButton({super.key, required this.onPressed});

  @override
  Widget build(BuildContext context) {
    final isCompact = MediaQuery.sizeOf(context).width < 430;
    final label = isCompact ? 'Neueste' : 'Zur neuesten Nachricht';

    return Semantics(
      button: true,
      label: 'Zur neuesten Nachricht springen',
      child: FloatingActionButton.extended(
        heroTag: 'latest-message-button',
        onPressed: onPressed,
        elevation: 2,
        backgroundColor: AppColors.careenaBubbleBackground.withValues(
          alpha: 0.92,
        ),
        foregroundColor: AppColors.careenaDark,
        icon: const Icon(Icons.keyboard_arrow_down),
        label: Text(label),
      ),
    );
  }
}
