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
        backgroundColor: const Color(0xFF26A69A),
        foregroundColor: Colors.white,
        icon: const Icon(Icons.keyboard_arrow_down),
        label: const Text('Zur neuesten Nachricht'),
      ),
    );
  }
}
