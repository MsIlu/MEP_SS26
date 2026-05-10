import 'package:flutter/material.dart';

/// Animated "thinking" indicator shown while the assistant is generating a response.
///
/// This widget displays:
/// - A pulsing dot animation
/// - A subtle loading state bubble
/// - A short status text indicating that the system is processing
class ThinkingBubble extends StatefulWidget {
  const ThinkingBubble({super.key});

  @override
  State<ThinkingBubble> createState() => _ThinkingBubbleState();
}

class _ThinkingBubbleState extends State<ThinkingBubble>
    with SingleTickerProviderStateMixin {
  late AnimationController controller;

  @override
  void initState() {
    super.initState();

    /// Controls the repeating animation loop for the loading dots
    controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    )..repeat();
  }

  @override
  void dispose() {
    // Dispose the controller to avoid memory leaks
    controller.dispose();
    super.dispose();
  }

  /// Builds a single animated dot with phase delay.
  ///
  /// Each dot uses the shared animation controller but applies
  /// an offset to create a wave-like loading effect.
  Widget _dot(double delay) {
    return AnimatedBuilder(
      animation: controller,
      builder: (_, __) {
        // Shift animation timing using the delay value
        final value = (controller.value + delay) % 1.0;

        // Smooth scaling animation
        final scale = 0.8 + (value < 0.5 ? value : 1 - value) * 0.6;

        // Smooth opacity animation
        final opacity = 0.3 + (value < 0.5 ? value : 1 - value) * 1.4;

        return Transform.scale(
          scale: scale,
          child: Opacity(
            opacity: opacity.clamp(0.3, 1),
            child: const Padding(
              padding: EdgeInsets.symmetric(horizontal: 3),
              child: CircleAvatar(
                radius: 3,
                backgroundColor: Colors.grey,
              ),
            ),
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Align(
      // Aligns the bubble to the left side like a chat message
    alignment: Alignment.centerLeft,

      child: AnimatedOpacity(
        // Smooth fade-in effect
        duration: const Duration(milliseconds: 300),
        opacity: 1,

        child: Container(
          // Outer spacing around the bubble
          margin: const EdgeInsets.symmetric(vertical: 6),
          // Inner spacing inside the bubble
          padding: const EdgeInsets.symmetric(
            horizontal: 14,
            vertical: 10,
          ),

          // Bubble styling
          decoration: BoxDecoration(
            color: Colors.white,

            // Rounded corners for chat bubble appearance
            borderRadius: BorderRadius.circular(16),

            // Soft shadow effect
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.06),
                blurRadius: 12,
                offset: const Offset(0, 4),
              )
            ],
          ),


          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              // Animated loading dots
              _dot(0.0),
              _dot(0.2),
              _dot(0.4),

              const SizedBox(width: 8),

              // Status text shown while response is being generated
              const Text(
                "Careena schreibt...",
                style: TextStyle(
                  fontSize: 13,
                  color: Colors.grey,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}