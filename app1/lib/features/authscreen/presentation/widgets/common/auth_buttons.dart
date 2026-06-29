import 'package:flutter/material.dart';
import 'package:app1/core/themes/app_colors.dart';
import '../../theme/auth_theme.dart';

/// Shared button widgets for Careena flows.
///
/// Keeping these together avoids one-file-per-tiny-widget churn while still
/// separating reusable controls from screen-level navigation.
class CareenaButton extends StatelessWidget {
  final String text;
  final VoidCallback? onPressed;
  final Color backgroundColor;
  final Color foregroundColor;
  final double borderRadius;
  final double elevation;
  final BorderSide? side;
  final double height;
  final double fontSize;

  const CareenaButton({
    super.key,
    required this.text,
    required this.onPressed,
    this.backgroundColor = AppColors.careenaPrimary,
    this.foregroundColor = AppColors.white,
    this.borderRadius = AuthTheme.buttonRadius,
    this.elevation = 0,
    this.side,
    this.height = 56,
    this.fontSize = 18,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      height: height,
      child: ElevatedButton(
        onPressed: onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: backgroundColor,
          foregroundColor: foregroundColor,
          elevation: elevation,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(borderRadius),
            side: side ?? BorderSide.none,
          ),
        ),
        child: FittedBox(
          fit: BoxFit.scaleDown,
          child: Text(
            text,
            style: TextStyle(
              fontSize: fontSize,
              fontWeight: FontWeight.w800,
              color: foregroundColor,
            ),
          ),
        ),
      ),
    );
  }
}

class AuthDivider extends StatelessWidget {
  final String text;

  const AuthDivider({super.key, this.text = 'oder'});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    final dividerColor = isDarkMode
        ? colorScheme.outlineVariant
        : AppColors.greyShade500;

    final textColor = isDarkMode
        ? colorScheme.onSurfaceVariant
        : AppColors.careenaBody;

    return Row(
      children: [
        Expanded(child: Divider(color: dividerColor, thickness: 1)),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 12),
          child: Text(text, style: TextStyle(fontSize: 14, color: textColor)),
        ),
        Expanded(child: Divider(color: dividerColor, thickness: 1)),
      ],
    );
  }
}

class SwitchAuthMode extends StatelessWidget {
  final String label;
  final String actionText;
  final VoidCallback onPressed;

  const SwitchAuthMode({
    super.key,
    required this.label,
    required this.actionText,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    final labelColor = isDarkMode
        ? colorScheme.onSurfaceVariant
        : AppColors.careenaBody;

    return Wrap(
      alignment: WrapAlignment.center,
      crossAxisAlignment: WrapCrossAlignment.center,
      children: [
        Text(label, style: TextStyle(color: labelColor)),
        AuthTextLink(text: actionText, onPressed: onPressed),
      ],
    );
  }
}

class AuthTextLink extends StatelessWidget {
  final String text;
  final VoidCallback onPressed;

  const AuthTextLink({super.key, required this.text, required this.onPressed});

  @override
  Widget build(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    final linkColor = isDarkMode
        ? AppColors.careenaAccentOnDark
        : AppColors.careenaTeal;

    return TextButton(
      onPressed: onPressed,
      style: TextButton.styleFrom(
        foregroundColor: linkColor,
        textStyle: const TextStyle(fontWeight: FontWeight.w700),
      ),
      child: Text(text),
    );
  }
}
