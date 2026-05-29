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
        icon: Icon(
          Icons.info_outline,
          color: Theme.of(context).brightness == Brightness.dark
              ? Theme.of(context).colorScheme.onSurfaceVariant
              : AppColors.careenaTitle,
        ),
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
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    final fillColor = isDarkMode
        ? const Color(0xFF263436)
        : AppColors.careenaNoteBackground;

    final borderColor = isDarkMode
        ? AppColors.toolbarButtonBackgroundDark.withValues(alpha: 0.55)
        : AppColors.careenaBorder;

    return TextFormField(
      controller: controller,
      readOnly: true,
      enableInteractiveSelection: false,
      style: TextStyle(
        color: colorScheme.onSurface,
      ),
      decoration: AuthTheme.inputDecoration(
        context: context,
        label: label,
        hint: hint,
      ).copyWith(
        filled: true,
        fillColor: fillColor,
        suffixIcon: AuthInfoButton(title: label, message: infoText),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AuthTheme.fieldRadius),
          borderSide: BorderSide(color: borderColor),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AuthTheme.fieldRadius),
          borderSide: BorderSide(color: borderColor),
        ),
      ),
    );
  }
}