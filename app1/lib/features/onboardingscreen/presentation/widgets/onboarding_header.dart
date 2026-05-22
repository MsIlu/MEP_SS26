import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// Branding row shown at the top of the onboarding screen.
class OnboardingHeader extends StatelessWidget {
  const OnboardingHeader({super.key});

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        // The logo and title scale down together so the row remains single-line
        // on narrow mobile screens.
        final isCompact = constraints.maxWidth < 360;
        final logoHeight = isCompact ? 52.0 : 65.0;
        final titleSize = isCompact ? 20.0 : 24.0;

        return Padding(
          padding: EdgeInsets.symmetric(horizontal: isCompact ? 14 : 22),
          child: Row(
            children: [
              Image.asset("assets/images/careena_logo.png", height: logoHeight),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  "MedBitAid v.1",
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: GoogleFonts.nunito(
                    fontSize: titleSize,
                    fontWeight: FontWeight.bold,
                    color: const Color(0xFF43B8BE),
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}