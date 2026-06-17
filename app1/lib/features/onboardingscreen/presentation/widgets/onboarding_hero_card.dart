import 'package:flutter/material.dart';

import 'package:app1/core/themes/app_colors.dart';
import '../../../authscreen/presentation/widgets/common/auth_buttons.dart';

/// Compact onboarding card that presents the primary chat call to action.
class OnboardingHeroCard extends StatelessWidget {
  /// Called when the user wants to start chatting with Careena.
  final VoidCallback onPressed;

  const OnboardingHeroCard({super.key, required this.onPressed});

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final isCompact = constraints.maxWidth < 380;
        final isDarkMode = Theme.of(context).brightness == Brightness.dark;
        final cardColor = isDarkMode
            ? AppColors.darkElevatedSurface
            : Colors.white;

        return Padding(
          padding: EdgeInsets.symmetric(horizontal: isCompact ? 10 : 13),
          child: Container(
            width: double.infinity,
            height: isCompact ? 304 : 326,
            padding: EdgeInsets.all(isCompact ? 12 : 14),
            decoration: BoxDecoration(
              color: cardColor,
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: AppColors.careenaGlow, width: 2),
              boxShadow: [
                BoxShadow(
                  color: AppColors.careenaGlow.withValues(
                    alpha: isDarkMode ? 0.15 : 0.08,
                  ),
                  blurRadius: isDarkMode ? 12 : 8,
                  spreadRadius: 1,
                ),
              ],
            ),
            child: Stack(
              clipBehavior: Clip.none,
              children: [
                Positioned(
                  left: 0,
                  top: 0,
                  width: isCompact ? 168 : 198,
                  child: _HeroCopy(isCompact: isCompact),
                ),
                Positioned(
                  right: isCompact ? -2 : 12,
                  top: isCompact ? 48 : 52,
                  width: isCompact ? 146 : 164,
                  child: Transform.rotate(
                    angle: -0.04,
                    child: _HeroSpeechBubble(isCompact: isCompact),
                  ),
                ),
                Positioned(
                  right: isCompact ? 0 : 18,
                  bottom: isCompact ? 18 : 18,
                  child: Image.asset(
                    'assets/images/careena_hi.png',
                    height: isCompact ? 136 : 156,
                  ),
                ),
                Positioned(
                  left: 0,
                  top: isCompact ? 164 : 180,
                  width: isCompact ? 220 : 250,
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      CareenaButton(
                        text: 'Jetzt mit Careena sprechen',
                        onPressed: onPressed,
                        backgroundColor: isDarkMode
                            ? AppColors.toolbarButtonBackgroundDark
                            : AppColors.careenaPrimary,
                        foregroundColor: isDarkMode
                            ? AppColors.toolbarButtonForegroundDark
                            : Colors.white,
                        borderRadius: 14,
                        height: isCompact ? 44 : 48,
                        side: const BorderSide(
                          color: AppColors.careenaGlow,
                          width: 2,
                        ),
                      ),
                      const SizedBox(height: 10),
                      const _DisclaimerLink(),
                    ],
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}

class _HeroCopy extends StatelessWidget {
  final bool isCompact;

  const _HeroCopy({required this.isCompact});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Die richtige Hilfe,\nzum richtigen Zeitpunkt.',
          style: TextStyle(
            fontSize: isCompact ? 20 : 23,
            fontWeight: FontWeight.w900,
            height: 1.14,
            color: isDarkMode
                ? Theme.of(context).colorScheme.onSurface
                : AppColors.careenaTitle,
          ),
        ),
        const SizedBox(height: 12),
        Container(
          width: 34,
          height: 5,
          decoration: BoxDecoration(
            color: AppColors.careenaPrimary,
            borderRadius: BorderRadius.circular(999),
          ),
        ),
        const SizedBox(height: 12),
        Text(
          'Beschreibe deine Beschwerden\nund erhalte deine persönliche\nHandlungsempfehlung.',
          style: TextStyle(
            fontSize: isCompact ? 11 : 12,
            fontWeight: FontWeight.w600,
            height: 1.28,
            color: isDarkMode ? colorScheme.onSurfaceVariant : Colors.black87,
          ),
        ),
      ],
    );
  }
}

class _DisclaimerLink extends StatelessWidget {
  const _DisclaimerLink();

  @override
  Widget build(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    final foregroundColor = isDarkMode
        ? Theme.of(context).colorScheme.onSurfaceVariant
        : AppColors.careenaMuted;

    return Center(
      child: TextButton.icon(
        onPressed: () => _showDisclaimerSheet(context),
        style: TextButton.styleFrom(
          foregroundColor: foregroundColor,
          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
          minimumSize: Size.zero,
          tapTargetSize: MaterialTapTargetSize.shrinkWrap,
          visualDensity: VisualDensity.compact,
        ),
        icon: const Icon(Icons.info_outline, size: 16),
        label: const Text(
          'Careena ersetzt keine ärztliche Diagnose.',
          textAlign: TextAlign.center,
          style: TextStyle(fontSize: 11.5, fontWeight: FontWeight.w700),
        ),
      ),
    );
  }

  void _showDisclaimerSheet(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      backgroundColor: isDarkMode
          ? AppColors.darkElevatedSurface
          : AppColors.careenaNoteBackground,
      builder: (context) => const _DisclaimerSheet(),
    );
  }
}

class _HeroSpeechBubble extends StatelessWidget {
  final bool isCompact;

  const _HeroSpeechBubble({required this.isCompact});

  @override
  Widget build(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    final bubbleColor = isDarkMode
        ? AppColors.onboardingBubbleDark
        : AppColors.lightCard;
    final borderColor = isDarkMode
        ? AppColors.onboardingBubbleBorderDark
        : AppColors.careenaBorder;

    return CustomPaint(
      painter: _HeroSpeechBubblePainter(
        fillColor: bubbleColor,
        borderColor: borderColor,
      ),
      child: Padding(
        padding: EdgeInsets.fromLTRB(
          isCompact ? 13 : 15,
          isCompact ? 11 : 13,
          isCompact ? 13 : 15,
          isCompact ? 24 : 26,
        ),
        child: Text(
          'Ich bin Careena!\nWie kann ich dir helfen?',
          style: TextStyle(
            fontSize: isCompact ? 10 : 11,
            height: 1.25,
            fontWeight: FontWeight.w800,
            color: AppColors.careenaBody,
          ),
        ),
      ),
    );
  }
}

class _HeroSpeechBubblePainter extends CustomPainter {
  final Color fillColor;
  final Color borderColor;

  const _HeroSpeechBubblePainter({
    required this.fillColor,
    required this.borderColor,
  });

  @override
  void paint(Canvas canvas, Size size) {
    const radius = 18.0;
    final bubbleBottom = size.height - 22;
    final tailTip = Offset(size.width * 0.64, size.height);
    final path = Path()
      ..moveTo(radius, 0)
      ..lineTo(size.width - radius, 0)
      ..quadraticBezierTo(size.width, 0, size.width, radius)
      ..lineTo(size.width, bubbleBottom - radius)
      ..quadraticBezierTo(
        size.width,
        bubbleBottom,
        size.width - 18,
        bubbleBottom,
      )
      ..lineTo(size.width * 0.76, bubbleBottom)
      ..quadraticBezierTo(
        size.width * 0.73,
        size.height - 8,
        tailTip.dx,
        tailTip.dy,
      )
      ..quadraticBezierTo(
        size.width * 0.58,
        size.height - 8,
        size.width * 0.48,
        bubbleBottom,
      )
      ..lineTo(radius, bubbleBottom)
      ..quadraticBezierTo(0, bubbleBottom, 0, bubbleBottom - radius)
      ..lineTo(0, radius)
      ..quadraticBezierTo(0, 0, radius, 0)
      ..close();

    canvas.drawShadow(
      path,
      AppColors.darkBackground.withValues(alpha: 0.08),
      8,
      false,
    );
    canvas.drawPath(path, Paint()..color = fillColor);
    canvas.drawPath(
      path,
      Paint()
        ..color = borderColor
        ..style = PaintingStyle.stroke
        ..strokeWidth = 1.2,
    );
  }

  @override
  bool shouldRepaint(covariant _HeroSpeechBubblePainter oldDelegate) {
    return fillColor != oldDelegate.fillColor ||
        borderColor != oldDelegate.borderColor;
  }
}

class _DisclaimerSheet extends StatelessWidget {
  const _DisclaimerSheet();

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(24, 4, 24, 28),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.info_outline, color: AppColors.careenaTeal),
                const SizedBox(width: 10),
                Text(
                  'Wichtiger Hinweis',
                  style: Theme.of(
                    context,
                  ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w900),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              'Careena unterstützt dich bei der Einordnung deiner Beschwerden. '
              'Die Hinweise ersetzen keine ärztliche Untersuchung, Diagnose '
              'oder Behandlung.',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                height: 1.4,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 18),
            Align(
              alignment: Alignment.centerRight,
              child: FilledButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('Verstanden'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
