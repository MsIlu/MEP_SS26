import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class OnboardingHeader extends StatelessWidget {
  const OnboardingHeader({super.key});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 22),

      child: Row(
        children: [
          Image.asset("assets/images/careena_logo.png", height: 65),

          const SizedBox(width: 10),

          Text(
            "MedBitAid v.1",

            style: GoogleFonts.nunito(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: const Color(0xFF43B8BE),
            ),
          ),
        ],
      ),
    );
  }
}