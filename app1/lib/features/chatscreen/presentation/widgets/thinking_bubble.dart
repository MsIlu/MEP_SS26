import 'package:flutter/material.dart';
import '../../../../core/config/app_assets.dart';
import '../themes/app_colors.dart';

/// Animated assistant bubble shown while a backend response is pending.
class ThinkingBubble extends StatefulWidget {
  /// Whether to show the extra hint for unusually slow responses.
  final bool showLongProcessingHint;

  const ThinkingBubble({super.key, this.showLongProcessingHint = false});

  @override
  State<ThinkingBubble> createState() => _ThinkingBubbleState();
}

/// Animation state for the assistant typing indicator.
class _ThinkingBubbleState extends State<ThinkingBubble>
    with SingleTickerProviderStateMixin {
  // Drives the three-dot pulse animation continuously while the bubble exists.
  late final AnimationController _controller;

  @override
  void initState() {
    super.initState();

    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  /// Builds one animated dot with a phase offset from the other dots.
  Widget _dot(double delay) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        // Offsetting the normalized controller value creates the wave-like
        // typing animation without needing three separate controllers.
        final value = (_controller.value + delay) % 1.0;
        final scale = 0.8 + (value < 0.5 ? value : 1 - value) * 0.6;
        final opacity = 0.3 + (value < 0.5 ? value : 1 - value) * 1.4;

        return Transform.scale(
          scale: scale,
          child: Opacity(
            opacity: opacity.clamp(0.3, 1),
            child: const Padding(
              padding: EdgeInsets.symmetric(horizontal: 3),
              child: CircleAvatar(radius: 3, backgroundColor: Colors.grey),
            ),
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          const CircleAvatar(
            radius: 16,
            backgroundColor: AppColors.careenaBubbleBackground,
            backgroundImage: AssetImage(AppAssets.careenaDoctor),
          ),
          const SizedBox(width: 8),
          AnimatedOpacity(
            duration: const Duration(milliseconds: 300),
            opacity: 1,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.06),
                    blurRadius: 12,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      _dot(0.0),
                      _dot(0.2),
                      _dot(0.4),
                      const SizedBox(width: 8),
                      const Text(
                        'Careena schreibt...',
                        style: TextStyle(fontSize: 13, color: Colors.grey),
                      ),
                    ],
                  ),
                  if (widget.showLongProcessingHint) ...[
                    const SizedBox(height: 8),
                    const Text(
                      'Die Antwort dauert etwas länger. Bitte bleiben Sie kurz im Chat.',
                      style: TextStyle(
                        fontSize: 12,
                        color: AppColors.careenaMuted,
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
