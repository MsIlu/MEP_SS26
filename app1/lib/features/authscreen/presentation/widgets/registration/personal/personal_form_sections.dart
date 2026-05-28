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
          hint: 'Mind. 8 Zeichen',
          obscureText: obscurePassword,
          validator: AuthValidators.newPassword,
          suffixIcon: PasswordVisibilityButton(
            obscurePassword: obscurePassword,
            onPressed: onTogglePassword,
          ),
        ),
        const SizedBox(height: _relatedFieldGap),
        AuthTextField(
          controller: confirmPasswordController,
          label: 'Passwort bestätigen',
          hint: 'Passwort wiederholen',
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