import 'package:flutter/material.dart';

import '../../../utils/birth_date_utils.dart';
import '../common/auth_buttons.dart';
import '../common/auth_layout.dart';
import 'birth_date/birth_date_field_with_age.dart';
import 'personal/personal_form_sections.dart';

const double _fieldGroupGap = 18;
const double _actionGap = 26;

/// First registration step: identity and account credentials.
class RegistrationPersonalDataStep extends StatefulWidget {
  final GlobalKey<FormState> formKey;
  final TextEditingController firstNameController;
  final TextEditingController lastNameController;
  final TextEditingController birthDateController;
  final TextEditingController emailController;
  final TextEditingController passwordController;
  final TextEditingController confirmPasswordController;
  final bool obscurePassword;
  final bool obscureConfirmPassword;
  final VoidCallback onTogglePassword;
  final VoidCallback onToggleConfirmPassword;
  final VoidCallback onNext;

  const RegistrationPersonalDataStep({
    super.key,
    required this.formKey,
    required this.firstNameController,
    required this.lastNameController,
    required this.birthDateController,
    required this.emailController,
    required this.passwordController,
    required this.confirmPasswordController,
    required this.obscurePassword,
    required this.obscureConfirmPassword,
    required this.onTogglePassword,
    required this.onToggleConfirmPassword,
    required this.onNext,
  });

  @override
  State<RegistrationPersonalDataStep> createState() =>
      _RegistrationPersonalDataStepState();
}

class _RegistrationPersonalDataStepState
    extends State<RegistrationPersonalDataStep> {
  late final TextEditingController _dayController;
  late final TextEditingController _monthController;
  late final TextEditingController _yearController;
  late final TextEditingController _ageController;
  late final FocusNode _dayFocusNode;
  late final FocusNode _monthFocusNode;
  late final FocusNode _yearFocusNode;

  @override
  void initState() {
    super.initState();
    _dayController = TextEditingController();
    _monthController = TextEditingController();
    _yearController = TextEditingController();
    _ageController = TextEditingController();
    _dayFocusNode = FocusNode();
    _monthFocusNode = FocusNode();
    _yearFocusNode = FocusNode();
    _populateBirthDateSegments();
    widget.birthDateController.addListener(_refreshAge);
  }

  @override
  void didUpdateWidget(RegistrationPersonalDataStep oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.birthDateController != widget.birthDateController) {
      oldWidget.birthDateController.removeListener(_refreshAge);
      widget.birthDateController.addListener(_refreshAge);
    }
  }

  @override
  void dispose() {
    widget.birthDateController.removeListener(_refreshAge);
    _dayController.dispose();
    _monthController.dispose();
    _yearController.dispose();
    _ageController.dispose();
    _dayFocusNode.dispose();
    _monthFocusNode.dispose();
    _yearFocusNode.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Form(
      key: widget.formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const AuthSectionTitle('Persönliche Daten eingeben'),
          const SizedBox(height: 16),
          PersonalNameFields(
            firstNameController: widget.firstNameController,
            lastNameController: widget.lastNameController,
          ),
          const SizedBox(height: _fieldGroupGap),
          BirthDateFieldWithAge(
            dayController: _dayController,
            monthController: _monthController,
            yearController: _yearController,
            ageController: _ageController,
            dayFocusNode: _dayFocusNode,
            monthFocusNode: _monthFocusNode,
            yearFocusNode: _yearFocusNode,
            birthDateController: widget.birthDateController,
            showValidation: _isBirthDateComplete,
            onChanged: _syncBirthDate,
          ),
          const SizedBox(height: _fieldGroupGap),
          PersonalAccountFields(
            emailController: widget.emailController,
            passwordController: widget.passwordController,
            confirmPasswordController: widget.confirmPasswordController,
            obscurePassword: widget.obscurePassword,
            obscureConfirmPassword: widget.obscureConfirmPassword,
            onTogglePassword: widget.onTogglePassword,
            onToggleConfirmPassword: widget.onToggleConfirmPassword,
          ),
          const SizedBox(height: _actionGap),
          CareenaButton(text: 'Weiter', onPressed: widget.onNext),
        ],
      ),
    );
  }

  void _refreshAge() {
    final age = BirthDateUtils.calculateAge(widget.birthDateController.text);
    _ageController.text = age == null ? '' : _formatAge(age);
    setState(() {});
  }

  String _formatAge(int age) {
    return age == 1 ? '1 Jahr' : '$age Jahre';
  }

  void _populateBirthDateSegments() {
    final parts = widget.birthDateController.text.split('.');
    if (parts.length == 3) {
      _dayController.text = parts[0];
      _monthController.text = parts[1];
      _yearController.text = parts[2];
    }
    _refreshAge();
  }

  void _syncBirthDate() {
    widget.birthDateController.text =
        '${_dayController.text}.${_monthController.text}.${_yearController.text}';
    _refreshAge();
  }

  bool get _isBirthDateComplete {
    return _dayController.text.length == 2 &&
        _monthController.text.length == 2 &&
        _yearController.text.length == 4;
  }
}
