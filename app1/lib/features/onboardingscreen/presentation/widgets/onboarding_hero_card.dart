import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'careena_chat_bubble.dart';

class OnboardingHeroCard extends StatelessWidget {
  final VoidCallback onPressed;

  const OnboardingHeroCard({super.key, required this.onPressed});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 13),

      child: Container(
        width: double.infinity,

        padding: const EdgeInsets.all(18),

        decoration: BoxDecoration(
          color: Colors.white,

          borderRadius: BorderRadius.circular(20),

          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.08),
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
                fontSize: 28,
                fontWeight: FontWeight.w800,
                height: 1.2,
                color: const Color(0xFF244C52),
              ),
            ),

            const SizedBox(height: 14),

            SizedBox(
              height: 230,
              width: double.infinity,

              child: Stack(
                children: [
                  Positioned(
                    left: 0,
                    top: 6,
                    width: MediaQuery.of(context).size.width * 0.48,

                    child: Text(
                      "Beschreibe deine Beschwerden\nund erhalte deine persönliche\nHandlungsempfehlung.",

                      style: GoogleFonts.nunito(
                        fontSize: 12,
                        color: Colors.black87,
                        height: 1.3,
                      ),
                    ),
                  ),

                  Positioned(
                    right: 0,
                    top: 40,
                    width: MediaQuery.of(context).size.width * 0.44,

                    child: const CareenaChatBubble(),
                  ),

                  Positioned(
                    bottom: 0,
                    left: 80,

                    child: Image.asset(
                      "assets/images/careena_hi.png",
                      height: 140,
                    ),
                  ),
                ],
              ),
            ),

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

                    side: const BorderSide(color: Color(0xFF00F0FF), width: 3),
                  ),
                ),

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
          ],
        ),
      ),
    );
  }
}
