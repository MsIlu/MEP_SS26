import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../../../../chatscreen/presentation/themes/app_colors.dart';

/// Short reassurance shown next to the explicit consent checkbox.
class PrivacyNote extends StatelessWidget {
  const PrivacyNote({super.key});

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: BoxDecoration(
        color: AppColors.careenaNoteBackground,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.careenaSoftAccent),
      ),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Row(
          children: [
            const Icon(Icons.lock_outline, color: AppColors.careenaTitle),
            const SizedBox(width: 10),
            Expanded(
              child: Text(
                'Deine Daten sind bei uns sicher und werden vertraulich behandelt.',
                style: GoogleFonts.nunito(
                  color: AppColors.careenaTitle,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}