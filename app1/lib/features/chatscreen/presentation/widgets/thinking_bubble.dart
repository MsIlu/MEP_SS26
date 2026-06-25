import 'package:flutter/material.dart';
import '../../../../core/config/app_assets.dart';
import 'package:app1/core/themes/app_colors.dart';

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
  Widget _dot(double delay, Color dotColor) {
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
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 3),
              child: CircleAvatar(radius: 3, backgroundColor: dotColor),
            ),
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    final bubbleColor = isDarkMode ? colorScheme.surface : Colors.white;
    final textColor = isDarkMode ? colorScheme.onSurface : Colors.grey;
    final hintTextColor = isDarkMode
        ? colorScheme.onSurfaceVariant
        : AppColors.careenaMuted;
    final dotColor = isDarkMode ? colorScheme.onSurfaceVariant : Colors.grey;
    final shadowColor = isDarkMode
        ? Colors.black.withValues(alpha: 0.15)
        : Colors.black.withValues(alpha: 0.06);

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
          Flexible(
            child: AnimatedOpacity(
              duration: const Duration(milliseconds: 300),
              opacity: 1,
              child: Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 14,
                  vertical: 10,
                ),
                decoration: BoxDecoration(
                  color: bubbleColor,
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: [
                    BoxShadow(
                      color: shadowColor,
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
                        _dot(0.0, dotColor),
                        _dot(0.2, dotColor),
                        _dot(0.4, dotColor),
                        const SizedBox(width: 8),
                        Flexible(
                          child: Text(
                            'Careena schreibt...',
                            overflow: TextOverflow.ellipsis,
                            style: TextStyle(fontSize: 13, color: textColor),
                          ),
                        ),
                      ],
                    ),
                    if (widget.showLongProcessingHint) ...[
                      const SizedBox(height: 8),
                      Text(
                        'Die Antwort dauert etwas länger. Bitte bleiben Sie kurz im Chat.',
                        softWrap: true,
                        style: TextStyle(fontSize: 12, color: hintTextColor),
                      ),
                    ],
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
