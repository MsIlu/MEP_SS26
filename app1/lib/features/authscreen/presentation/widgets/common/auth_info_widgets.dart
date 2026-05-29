import 'package:flutter/material.dart';
import '../../../../chatscreen/presentation/themes/app_colors.dart';
import '../../theme/auth_theme.dart';

/// Shared info icon that shows the same explanation on hover and tap.
class AuthInfoButton extends StatelessWidget {
  final String title;
  final String message;
  final VisualDensity? visualDensity;

  const AuthInfoButton({
    super.key,
    required this.title,
    required this.message,
    this.visualDensity,
  });

  @override
  Widget build(BuildContext context) {
    return Tooltip(
      message: message,
      child: IconButton(
        tooltip: message,
        visualDensity: visualDensity,
        icon: const Icon(Icons.info_outline, color: AppColors.careenaTitle),
        onPressed: () => _showInfoDialog(context),
      ),
    );
  }

  void _showInfoDialog(BuildContext context) {
    showDialog<void>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text(title),
          content: Text(message),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Verstanden'),
            ),
          ],
        );
      },
    );
  }
}

/// Read-only calculated value field with the same visual treatment everywhere.
class AuthCalculatedField extends StatelessWidget {
  final TextEditingController controller;
  final String label;
  final String hint;
  final String infoText;

  const AuthCalculatedField({
    super.key,
    required this.controller,
    required this.label,
    required this.hint,
    required this.infoText,
  });

  @override
  Widget build(BuildContext context) {
    return TextFormField(
      controller: controller,
      readOnly: true,
      enableInteractiveSelection: false,
      decoration: AuthTheme.inputDecoration(context: context, label: label, hint: hint).copyWith(
        filled: true,
        fillColor: AppColors.careenaNoteBackground,
        suffixIcon: AuthInfoButton(title: label, message: infoText),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AuthTheme.fieldRadius),
          borderSide: const BorderSide(color: AppColors.careenaBorder),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AuthTheme.fieldRadius),
          borderSide: const BorderSide(color: AppColors.careenaBorder),
        ),
      ),
    );
  }
}