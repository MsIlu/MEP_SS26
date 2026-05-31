import 'package:flutter/material.dart';

import '../../../chatscreen/controllers/chat_controller.dart';
import '../../../homescreen/presentation/screens/home_screen.dart';
import '../view_models/registration_form_controller.dart';
import '../widgets/common/auth_buttons.dart';
import '../widgets/common/auth_layout.dart';
import '../widgets/registration/registration_health_step.dart';
import '../widgets/registration/registration_personal_step.dart';
import '../widgets/registration/registration_review_step.dart';
import '../widgets/registration/registration_step_indicator.dart';
import 'login_screen.dart';
import '../../../../core/themes/theme_controller.dart';

/// Multi-step registration flow based on the prototype screens.
class RegistrationScreen extends StatefulWidget {
  final ChatController chatController;
  final ThemeController themeController;

  const RegistrationScreen({
    super.key,
    required this.chatController,
    required this.themeController,
  });

  @override
  State<RegistrationScreen> createState() => _RegistrationScreenState();
}

class _RegistrationScreenState extends State<RegistrationScreen> {
  final _form = RegistrationFormController();
  int _step = 0;

  @override
  void dispose() {
    _form.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AuthPageScaffold(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          AuthTopBar(
            onBack: _goBack,
            showBrand: false,
            onToggleTheme: widget.themeController.toggleTheme,
            isDarkMode: widget.themeController.isDarkMode,
          ),
          const SizedBox(height: 22),
          AuthIntro(title: 'Konto erstellen', subtitle: _subtitle),
          const SizedBox(height: 22),
          RegistrationStepIndicator(
            currentStep: _step,
            onStepSelected: _goToCompletedStep,
          ),
          const SizedBox(height: 26),
          AnimatedSwitcher(
            duration: const Duration(milliseconds: 180),
            child: KeyedSubtree(key: ValueKey<int>(_step), child: _buildStep()),
          ),
          const SizedBox(height: 16),
          SwitchAuthMode(
            label: 'Du hast bereits ein Konto?',
            actionText: 'Anmelden',
            onPressed: _openLogin,
          ),
        ],
      ),
    );
  }

  String get _subtitle {
    if (_step == 2) {
      return 'Überprüfe deine Daten, um Fehler zu vermeiden.';
    }
    return 'Erstelle ein Konto, um Careena, deine virtuelle Gesundheitsassistentin, optimal zu nutzen.';
  }

  Widget _buildStep() {
    return switch (_step) {
      0 => RegistrationPersonalDataStep(
        formKey: _form.personalFormKey,
        firstNameController: _form.firstNameController,
        lastNameController: _form.lastNameController,
        birthDateController: _form.birthDateController,
        emailController: _form.emailController,
        passwordController: _form.passwordController,
        confirmPasswordController: _form.confirmPasswordController,
        obscurePassword: _form.obscurePassword,
        obscureConfirmPassword: _form.obscureConfirmPassword,
        onTogglePassword: () {
          setState(_form.togglePasswordVisibility);
        },
        onToggleConfirmPassword: () {
          setState(_form.toggleConfirmPasswordVisibility);
        },
        onNext: _nextFromPersonal,
      ),
      1 => RegistrationHealthDataStep(
        formKey: _form.healthFormKey,
        selectedSex: _form.sex,
        selectedConditions: _form.conditions,
        heightController: _form.heightController,
        weightController: _form.weightController,
        notesController: _form.notesController,
        onSexChanged: (value) => setState(() => _form.sex = value),
        onConditionChanged: _updateCondition,
        onNext: _nextFromHealth,
      ),
      _ => RegistrationReviewStep(
        personalItems: _form.personalReviewItems,
        healthItems: _form.healthReviewItems,
        hasAcceptedConsent: _form.hasAcceptedConsent,
        onConsentChanged: _updateConsent,
        onEditPersonalData: () => _goToCompletedStep(0),
        onEditHealthData: () => _goToCompletedStep(1),
        onSubmit: _finishRegistration,
      ),
    };
  }

  void _goBack() {
    if (_step == 0) {
      Navigator.of(context).pop();
      return;
    }
    setState(() => _step -= 1);
  }

  void _openLogin() {
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(
        builder: (context) => LoginScreen(
          chatController: widget.chatController,
          themeController: widget.themeController,
        ),
      ),
    );
  }

  void _updateCondition(String condition, bool selected) {
    setState(() => _form.updateCondition(condition, selected));
  }

  void _updateConsent(bool accepted) {
    setState(() => _form.updateConsent(accepted));
  }

  void _goToCompletedStep(int step) {
    if (step < _step) {
      setState(() => _step = step);
    }
  }

  void _nextFromPersonal() {
    if (_form.isPersonalStepValid) {
      setState(() => _step = 1);
    }
  }

  void _nextFromHealth() {
    if (_form.isHealthStepValid) {
      setState(() => _step = 2);
    }
  }

  void _finishRegistration() {
    if (!_form.hasAcceptedConsent) {
      return;
    }

    // TODO(backend): Submit registration data, consent timestamp, and health
    // TODO: profile to the API before creating the authenticated Home session.
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(
        builder: (context) => HomeScreen(
          controller: widget.chatController,
          themeController: widget.themeController,
        ),
      ),
    );
  }
}