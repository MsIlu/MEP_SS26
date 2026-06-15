import 'package:flutter/material.dart';

class AppGuideSpotlightPainter extends CustomPainter {
  final Rect spotlight;
  final double radius;
  final Color scrimColor;
  final Color outlineColor;

  const AppGuideSpotlightPainter({
    required this.spotlight,
    required this.radius,
    required this.scrimColor,
    required this.outlineColor,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final spotlightRRect = RRect.fromRectAndRadius(
      spotlight,
      Radius.circular(radius),
    );

    // Clear the spotlight from an isolated scrim layer so the original screen
    // remains fully visible inside the rounded focus area.
    canvas.saveLayer(Offset.zero & size, Paint());
    canvas.drawRect(Offset.zero & size, Paint()..color = scrimColor);
    canvas.drawRRect(spotlightRRect, Paint()..blendMode = BlendMode.clear);
    canvas.restore();

    canvas.drawRRect(
      spotlightRRect,
      Paint()
        ..color = outlineColor
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2,
    );
  }

  @override
  bool shouldRepaint(covariant AppGuideSpotlightPainter oldDelegate) {
    return spotlight != oldDelegate.spotlight ||
        radius != oldDelegate.radius ||
        scrimColor != oldDelegate.scrimColor ||
        outlineColor != oldDelegate.outlineColor;
  }
}
