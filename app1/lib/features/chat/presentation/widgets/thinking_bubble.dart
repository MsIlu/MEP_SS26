import 'package:flutter/material.dart';
import '../../../../core/config/app_assets.dart';

class ThinkingBubble extends StatefulWidget {
  final bool showLongProcessingHint;
  final VoidCallback? onCancelGeneration;

  const ThinkingBubble({
    super.key,
    this.showLongProcessingHint = false,
    this.onCancelGeneration,
  });

  @override
  State<ThinkingBubble> createState() => _ThinkingBubbleState();
}

class _ThinkingBubbleState extends State<ThinkingBubble>
    with SingleTickerProviderStateMixin {
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

  Widget _dot(double delay) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
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
            backgroundColor: Color(0xFFE7F5F3),
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
                        color: Color(0xFF6B7C80),
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),

          if (widget.onCancelGeneration != null) ...[
            const SizedBox(width: 6),
            InkWell(
              onTap: widget.onCancelGeneration,
              borderRadius: BorderRadius.circular(20),
              child: Container(
                width: 20,
                height: 20,
                decoration: const BoxDecoration(
                  color: Color(0xFFF1615F),
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.close_rounded,
                  size: 14,
                  color: Colors.white,
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }
}