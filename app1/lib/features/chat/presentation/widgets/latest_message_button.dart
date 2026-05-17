import 'package:flutter/material.dart';

class LatestMessageButton extends StatelessWidget {
  final VoidCallback onPressed;

  const LatestMessageButton({super.key, required this.onPressed});

  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: true,
      label: 'Zur neuesten Nachricht springen',
      child: FloatingActionButton.extended(
        heroTag: 'latest-message-button',
        onPressed: onPressed,
        elevation: 2,
        backgroundColor: const Color(0xFFE7F5F3).withValues(alpha: 0.92),
        foregroundColor: const Color(0xFF2C5358),
        icon: const Icon(Icons.keyboard_arrow_down),
        label: const Text('Zur neuesten Nachricht'),
      ),
    );
  }
}
