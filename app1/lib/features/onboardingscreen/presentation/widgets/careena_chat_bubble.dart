import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../chatscreen/presentation/themes/app_colors.dart';

/// Small speech bubble introducing Careena on the onboarding hero card.
class CareenaChatBubble extends StatelessWidget {
  const CareenaChatBubble({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(10),

      decoration: BoxDecoration(
        color: Colors.white,

        borderRadius: BorderRadius.circular(14),

        border: Border.all(color: AppColors.careenaBorder, width: 1),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.03),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Text(
        "Ich bin Careena!\nDeine persönliche\nKI-Gesundheitsassistentin.",

        style: GoogleFonts.nunito(
          fontSize: 12,
          height: 1.2,
          color: AppColors.careenaTitle,
        ),
      ),
    );
  }
}