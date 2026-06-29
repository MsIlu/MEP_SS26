import 'package:flutter/material.dart';

import 'package:app1/core/themes/app_colors.dart';

/// Small speech bubble shown on the onboarding hero card.
class CareenaChatBubble extends StatelessWidget {
  final String? title;
  final String text;
  final Widget? footer;
  final double fontSize;
  final bool useDarkSurfaceInDarkMode;

  const CareenaChatBubble({
    super.key,
    this.title,
    this.text =
        'Ich bin Careena!\nDeine persönliche\nKI-Gesundheits-\nassistentin.',
    this.footer,
    this.fontSize = 12,
    this.useDarkSurfaceInDarkMode = false,
  });

  @override
  Widget build(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    final usesDarkSurface = isDarkMode && useDarkSurfaceInDarkMode;

    final bubbleColor = usesDarkSurface
        ? AppColors.darkElevatedSurface
        : isDarkMode
        ? AppColors.onboardingBubbleDark
        : AppColors.lightCard;

    final textColor = usesDarkSurface
        ? AppColors.darkTextPrimary
        : isDarkMode
        ? AppColors.careenaTitle
        : AppColors.careenaBody;

    final borderColor = usesDarkSurface
        ? AppColors.toolbarButtonBackgroundDark
        : isDarkMode
        ? AppColors.onboardingBubbleBorderDark
        : AppColors.careenaBorder;

    return CustomPaint(
      painter: _SpeechBubblePainter(
        fillColor: bubbleColor,
        borderColor: borderColor,
        shadowOpacity: isDarkMode ? 0.16 : 0.08,
      ),
      child: Padding(
        padding: const EdgeInsets.fromLTRB(30, 18, 18, 18),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            if (title != null) ...[
              Text(
                title!,
                style: TextStyle(
                  fontSize: fontSize + 2,
                  height: 1.2,
                  fontWeight: FontWeight.w900,
                  color: textColor,
                ),
              ),
              const SizedBox(height: 6),
            ],
            Text(
              text,
              style: TextStyle(
                fontSize: fontSize,
                height: 1.3,
                fontWeight: FontWeight.w700,
                color: textColor,
              ),
            ),
            if (footer != null) ...[const SizedBox(height: 10), footer!],
          ],
        ),
      ),
    );
  }
}

class _SpeechBubblePainter extends CustomPainter {
  final Color fillColor;
  final Color borderColor;
  final double shadowOpacity;

  const _SpeechBubblePainter({
    required this.fillColor,
    required this.borderColor,
    required this.shadowOpacity,
  });

  @override
  void paint(Canvas canvas, Size size) {
    const radius = 18.0;
    const leftInset = 18.0;

    final path = Path()
      ..moveTo(leftInset + radius, 0)
      // top
      ..lineTo(size.width - radius, 0)
      ..quadraticBezierTo(size.width, 0, size.width, radius)
      // right
      ..lineTo(size.width, size.height - radius)
      ..quadraticBezierTo(
        size.width,
        size.height,
        size.width - radius,
        size.height,
      )
      // bottom
      ..lineTo(leftInset + radius, size.height)
      ..quadraticBezierTo(
        leftInset,
        size.height,
        leftInset,
        size.height - radius,
      )
      // softer, rounded tail on the left
      ..lineTo(leftInset, size.height * 0.68)
      ..quadraticBezierTo(
        leftInset - 4,
        size.height * 0.74,
        leftInset - 18,
        size.height * 0.82,
      )
      ..quadraticBezierTo(
        leftInset - 8,
        size.height * 0.82,
        leftInset,
        size.height * 0.78,
      )
      // left side back up
      ..lineTo(leftInset, radius)
      ..quadraticBezierTo(leftInset, 0, leftInset + radius, 0)
      ..close();

    canvas.drawShadow(
      path,
      AppColors.darkBackground.withValues(alpha: shadowOpacity),
      10,
      false,
    );

    final fillPaint = Paint()..color = fillColor;
    canvas.drawPath(path, fillPaint);

    final borderPaint = Paint()
      ..color = borderColor
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.2;

    canvas.drawPath(path, borderPaint);
  }

  @override
  bool shouldRepaint(covariant _SpeechBubblePainter oldDelegate) {
    return fillColor != oldDelegate.fillColor ||
        borderColor != oldDelegate.borderColor ||
        shadowOpacity != oldDelegate.shadowOpacity;
  }
}
