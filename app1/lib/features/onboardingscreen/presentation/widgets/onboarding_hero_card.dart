import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'careena_chat_bubble.dart';

class OnboardingHeroCard extends StatelessWidget {
  final VoidCallback onPressed;

  const OnboardingHeroCard({super.key, required this.onPressed});

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final isCompact = constraints.maxWidth < 380;
        final horizontalMargin = isCompact ? 12.0 : 13.0;

        return Padding(
          padding: EdgeInsets.symmetric(horizontal: horizontalMargin),
          child: Container(
            width: double.infinity,
            padding: EdgeInsets.all(isCompact ? 16 : 18),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.08),
                  blurRadius: 10,
                  offset: const Offset(0, 5),
                ),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  "Die richtige Hilfe,\nzum richtigen\nZeitpunkt.",
                  style: GoogleFonts.nunito(
                    fontSize: isCompact ? 24 : 28,
                    fontWeight: FontWeight.w800,
                    height: 1.2,
                    color: const Color(0xFF244C52),
                  ),
                ),
                const SizedBox(height: 14),
                isCompact ? const _CompactHeroBody() : const _RegularHeroBody(),
                const SizedBox(height: 16),
                SizedBox(
                  width: double.infinity,
                  height: 58,
                  child: ElevatedButton(
                    onPressed: onPressed,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF37AEB5),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(40),
                        side: const BorderSide(
                          color: Color(0xFF00F0FF),
                          width: 3,
                        ),
                      ),
                    ),
                    child: FittedBox(
                      fit: BoxFit.scaleDown,
                      child: Text(
                        "Jetzt mit Careena sprechen",
                        style: GoogleFonts.nunito(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                    ),
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

class _RegularHeroBody extends StatelessWidget {
  const _RegularHeroBody();

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 230,
      width: double.infinity,
      child: LayoutBuilder(
        builder: (context, constraints) {
          return Stack(
            children: [
              Positioned(
                left: 0,
                top: 6,
                width: constraints.maxWidth * 0.48,
                child: const _HeroDescription(),
              ),
              Positioned(
                right: 0,
                top: 40,
                width: constraints.maxWidth * 0.44,
                child: const CareenaChatBubble(),
              ),
              Positioned(
                bottom: 0,
                left: constraints.maxWidth * 0.24,
                child: Image.asset("assets/images/careena_hi.png", height: 140),
              ),
            ],
          );
        },
      ),
    );
  }
}

class _CompactHeroBody extends StatelessWidget {
  const _CompactHeroBody();

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const _HeroDescription(),
        const SizedBox(height: 12),
        const Align(
          alignment: Alignment.centerRight,
          child: FractionallySizedBox(
            widthFactor: 0.78,
            child: CareenaChatBubble(),
          ),
        ),
        const SizedBox(height: 6),
        Center(child: Image.asset("assets/images/careena_hi.png", height: 118)),
      ],
    );
  }
}

class _HeroDescription extends StatelessWidget {
  const _HeroDescription();

  @override
  Widget build(BuildContext context) {
    return Text(
      "Beschreibe deine Beschwerden\nund erhalte deine persönliche\nHandlungsempfehlung.",
      style: GoogleFonts.nunito(
        fontSize: 12,
        color: Colors.black87,
        height: 1.3,
      ),
    );
  }
}