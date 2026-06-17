import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../../../utils/auth_validators.dart';
import '../../common/auth_fields.dart';
import '../../common/auth_layout.dart';

const double _relatedFieldGap = 10;
const double _accountGroupGap = 20;
final _nameInputFormatters = [FilteringTextInputFormatter.deny(RegExp(r'\d'))];

/// Name inputs for the personal-data registration step.
class PersonalNameFields extends StatelessWidget {
  final TextEditingController firstNameController;
  final TextEditingController lastNameController;

  const PersonalNameFields({
    super.key,
    required this.firstNameController,
    required this.lastNameController,
  });

  @override
  Widget build(BuildContext context) {
    return AdaptiveFieldRow(
      horizontalGap: _relatedFieldGap,
      verticalGap: _relatedFieldGap,
      children: [
        AuthTextField(
          controller: firstNameController,
          label: 'Vorname',
          hint: 'Vorname',
          keyboardType: TextInputType.name,
          textInputAction: TextInputAction.next,
          inputFormatters: _nameInputFormatters,
          validator: AuthValidators.nameText,
        ),
        AuthTextField(
          controller: lastNameController,
          label: 'Nachname',
          hint: 'Nachname',
          keyboardType: TextInputType.name,
          textInputAction: TextInputAction.next,
          inputFormatters: _nameInputFormatters,
          validator: AuthValidators.nameText,
        ),
      ],
    );
  }
}

/// Account inputs for the personal-data registration step.
class PersonalAccountFields extends StatelessWidget {
  final TextEditingController emailController;
  final TextEditingController passwordController;
  final TextEditingController confirmPasswordController;
  final bool obscurePassword;
  final bool obscureConfirmPassword;
  final VoidCallback onTogglePassword;
  final VoidCallback onToggleConfirmPassword;

  const PersonalAccountFields({
    super.key,
    required this.emailController,
    required this.passwordController,
    required this.confirmPasswordController,
    required this.obscurePassword,
    required this.obscureConfirmPassword,
    required this.onTogglePassword,
    required this.onToggleConfirmPassword,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        AuthTextField(
          controller: emailController,
          label: 'E-Mail-Adresse',
          hint: 'name@beispiel.de',
          keyboardType: TextInputType.emailAddress,
          textInputAction: TextInputAction.next,
          validator: AuthValidators.email,
        ),
        const SizedBox(height: _accountGroupGap),
        AuthTextField(
          controller: passwordController,
          label: 'Passwort',
          hint: 'Passwort',
          obscureText: obscurePassword,
          validator: AuthValidators.newPassword,
          suffixIcon: PasswordVisibilityButton(
            obscurePassword: obscurePassword,
            onPressed: onTogglePassword,
          ),
        ),
        const SizedBox(height: 8),
        PasswordRequirementChecklist(passwordController: passwordController),
        const SizedBox(height: _relatedFieldGap),
        AuthTextField(
          controller: confirmPasswordController,
          label: 'Passwort bestätigen',
          hint: 'Passwort bestätigen',
          obscureText: obscureConfirmPassword,
          validator: (value) => AuthValidators.passwordConfirmation(
            value,
            passwordController.text,
          ),
          suffixIcon: PasswordVisibilityButton(
            obscurePassword: obscureConfirmPassword,
            onPressed: onToggleConfirmPassword,
          ),
        ),
      ],
    );
  }
}

class PasswordRequirementChecklist extends StatelessWidget {
  final TextEditingController passwordController;

  const PasswordRequirementChecklist({
    super.key,
    required this.passwordController,
  });

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<TextEditingValue>(
      valueListenable: passwordController,
      builder: (context, value, _) {
        final password = value.text;
        final missingRequirements = [
          if (!AuthValidators.hasMinPasswordLength(password))
            'Mindestens 8 Zeichen',
          if (!AuthValidators.hasPasswordLowercase(password))
            'Ein Kleinbuchstabe',
          if (!AuthValidators.hasPasswordUppercase(password))
            'Ein Großbuchstabe',
          if (!AuthValidators.hasPasswordNumber(password)) 'Eine Zahl',
          if (!AuthValidators.hasPasswordSpecialCharacter(password))
            'Ein Sonderzeichen',
        ];

        if (missingRequirements.isEmpty) {
          return const SizedBox.shrink();
        }

        return Padding(
          padding: const EdgeInsets.only(left: 18, right: 18),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              for (final requirement in missingRequirements)
                _PasswordRequirement(text: requirement),
            ],
          ),
        );
      },
    );
  }
}

class _PasswordRequirement extends StatelessWidget {
  final String text;

  const _PasswordRequirement({required this.text});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    final color = colorScheme.onSurfaceVariant.withValues(
      alpha: isDarkMode ? 0.68 : 0.58,
    );

    return Padding(
      padding: const EdgeInsets.only(bottom: 5),
      child: Text(
        text,
        style: TextStyle(
          fontSize: 13,
          fontWeight: FontWeight.w600,
          color: color,
        ),
      ),
    );
  }
}
