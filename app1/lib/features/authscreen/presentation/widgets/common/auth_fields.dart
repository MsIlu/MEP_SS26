import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../theme/auth_theme.dart';

/// Shared form field widgets for login and registration.
class AuthTextField extends StatelessWidget {
  final TextEditingController controller;
  final String label;
  final String hint;
  final TextInputType? keyboardType;
  final TextInputAction? textInputAction;
  final bool obscureText;
  final Widget? suffixIcon;
  final String? suffixText;
  final int? maxLength;
  final int maxLines;
  final List<TextInputFormatter>? inputFormatters;
  final String? Function(String?)? validator;
  final ValueChanged<String>? onChanged;
  final ValueChanged<String>? onFieldSubmitted;

  const AuthTextField({
    super.key,
    required this.controller,
    required this.label,
    required this.hint,
    this.keyboardType,
    this.textInputAction,
    this.obscureText = false,
    this.suffixIcon,
    this.suffixText,
    this.maxLength,
    this.maxLines = 1,
    this.inputFormatters,
    this.validator,
    this.onChanged,
    this.onFieldSubmitted,
  });

  @override
  Widget build(BuildContext context) {
    return TextFormField(
      controller: controller,
      keyboardType: keyboardType,
      textInputAction: textInputAction,
      obscureText: obscureText,
      maxLength: maxLength,
      maxLines: maxLines,
      inputFormatters: inputFormatters,
      validator: validator,
      onChanged: onChanged,
      onFieldSubmitted: onFieldSubmitted,
      decoration: AuthTheme.inputDecoration(
        context: context,
        label: label,
        hint: hint,
        suffixIcon: suffixIcon,
        suffixText: suffixText,
      ),
    );
  }
}

class PasswordVisibilityButton extends StatelessWidget {
  final bool obscurePassword;
  final VoidCallback onPressed;

  const PasswordVisibilityButton({
    super.key,
    required this.obscurePassword,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return IconButton(
      tooltip: obscurePassword ? 'Passwort anzeigen' : 'Passwort verbergen',
      onPressed: onPressed,
      icon: Icon(
        obscurePassword
            ? Icons.visibility_outlined
            : Icons.visibility_off_outlined,
      ),
    );
  }
}