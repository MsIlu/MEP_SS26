import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// Full-width onboarding button used for login and registration actions.
class AuthButton extends StatelessWidget {
  /// Button label shown to the user.
  final String text;

  /// Action executed when the button is pressed.
  final VoidCallback onPressed;

  const AuthButton({super.key, required this.text, required this.onPressed});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      height: 56,
      child: ElevatedButton(
        onPressed: onPressed,

        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.white,

          elevation: 2,

          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(22),
          ),
        ),

        child: Text(
          text,

          style: GoogleFonts.nunito(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: const Color(0xFF1D2B34),
          ),
        ),
      ),
    );
  }
}