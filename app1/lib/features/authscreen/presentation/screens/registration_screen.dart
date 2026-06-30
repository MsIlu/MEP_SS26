import 'package:app1/app/app_page_store.dart';
import 'package:app1/features/symptom_diary/data/symptom_repository.dart';
import 'package:flutter/material.dart';

import '../../../app_guide/data/app_guide_store.dart';
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
import '../../../onboardingscreen/presentation/screens/onboarding_screen.dart';
import '../../../../core/themes/theme_controller.dart';
import '../../state/auth_session.dart';
import '../../data/auth_api_service.dart';
import '../../../../core/widgets/careena_page_header.dart';

/// Multi-step registration flow based on the prototype screens.
class RegistrationScreen extends StatefulWidget {
  final ChatController chatController;
  final ThemeController themeController;
  final AuthSession authSession;
  final AuthApiService authApiService;
  final SymptomRepository symptomRepository;

  const RegistrationScreen({
    super.key,
    required this.chatController,
    required this.themeController,
    required this.authSession,
    required this.authApiService,
    required this.symptomRepository,
  });

  @override
  State<RegistrationScreen> createState() => _RegistrationScreenState();
}

class _RegistrationScreenState extends State<RegistrationScreen> {
  final _form = RegistrationFormController();
  int _step = 0;
  bool _isSubmitting = false;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    AppPageStore.saveCurrentPage(AppPage.registration);
  }

  @override
  void dispose() {
    _form.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AuthPageScaffold(
      fixedHeader: CareenaPageHeader(
        title: 'Konto erstellen',
        onBack: _goBack,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(_subtitle),
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
          if (_errorMessage != null) ...[
            const SizedBox(height: 12),
            Text(
              _errorMessage!,
              style: TextStyle(
                color: Theme.of(context).colorScheme.error,
                fontWeight: FontWeight.w600,
              ),
              textAlign: TextAlign.center,
            ),
          ],
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

  String? _normalizeBirthDate(String rawValue) {
    final value = rawValue.trim();

    if (value.isEmpty) {
      return null;
    }

    // Already backend-compatible: YYYY-MM-DD
    final backendFormat = RegExp(r'^\d{4}-\d{2}-\d{2}$');
    if (backendFormat.hasMatch(value)) {
      return value;
    }

    // German UI format: DD.MM.YYYY -> YYYY-MM-DD
    final germanFormat = RegExp(r'^(\d{2})\.(\d{2})\.(\d{4})$');
    final match = germanFormat.firstMatch(value);

    if (match == null) {
      return value;
    }

    final day = match.group(1)!;
    final month = match.group(2)!;
    final year = match.group(3)!;

    return '$year-$month-$day';
  }

  String? _biologicalSexForBackend(String value) {
    return switch (value) {
      'Weiblich' => 'female',
      'Männlich' => 'male',
      _ => null,
    };
  }

  int? _heightForBackend(String value) {
    return int.tryParse(value.trim());
  }

  double? _weightForBackend(String value) {
    return double.tryParse(value.trim().replaceAll(',', '.'));
  }

  String? _conditionsForBackend() {
    if (_form.conditions.isEmpty) {
      return null;
    }

    return _form.conditions.join(', ');
  }

  String? _notesForBackend() {
    final notes = _form.notesController.text.trim();
    return notes.isEmpty ? null : notes;
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
        onSubmit: _isSubmitting ? () {} : _finishRegistration,
      ),
    };
  }

  Future<void> _goBack() async {
    if (_step == 0) {
      await AppPageStore.saveCurrentPage(AppPage.onboarding);
      if (!mounted) return;
      Navigator.of(context, rootNavigator: true).pushAndRemoveUntil(
        MaterialPageRoute(
          builder: (context) => OnboardingScreen(
            chatController: widget.chatController,
            themeController: widget.themeController,
            authSession: widget.authSession,
            authApiService: widget.authApiService,
            symptomRepository: widget.symptomRepository,
          ),
        ),
        (route) => false,
      );
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
          authSession: widget.authSession,
          authApiService: widget.authApiService,
          symptomRepository: widget.symptomRepository,
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

  Future<void> _finishRegistration() async {
    if (!_form.hasAcceptedConsent) {
      setState(() {
        _errorMessage = 'Bitte akzeptiere die Einwilligung, um fortzufahren.';
      });
      return;
    }

    setState(() {
      _isSubmitting = true;
      _errorMessage = null;
    });

    try {
      final displayName =
          '${_form.firstNameController.text.trim()} ${_form.lastNameController.text.trim()}'
              .trim();

      final authResponse = await widget.authApiService.register(
        email: _form.emailController.text.trim(),
        password: _form.passwordController.text,
        displayName: displayName,
        dateOfBirth: _normalizeBirthDate(_form.birthDateController.text),
        biologicalSex: _biologicalSexForBackend(_form.sex),
        heightCm: _heightForBackend(_form.heightController.text),
        weightKg: _weightForBackend(_form.weightController.text),
        relevantPreconditionsSummary: _conditionsForBackend(),
        symptomDiarySummary: _notesForBackend(),
      );

      widget.authSession.setAuthResponse(authResponse);

      if (!mounted) return;

      final guideStore = AppGuideStore();
      final hasCompletedGuide = await guideStore.isCompleted(
        AppGuideStore.accountKey(authResponse.account.id),
      );

      if (!mounted) return;

      Navigator.of(context).pushReplacement(
        MaterialPageRoute(
          builder: (context) =>
              _buildHomeScreen(startGuide: !hasCompletedGuide),
        ),
      );
    } catch (_) {
      if (!mounted) return;

      setState(() {
        _errorMessage =
            'Registrierung fehlgeschlagen. Bitte überprüfe deine Eingaben.';
      });
    } finally {
      if (mounted) {
        setState(() {
          _isSubmitting = false;
        });
      }
    }
  }

  HomeScreen _buildHomeScreen({bool startGuide = false}) {
    return HomeScreen(
      controller: widget.chatController,
      themeController: widget.themeController,
      authSession: widget.authSession,
      authApiService: widget.authApiService,
      startGuide: startGuide,
    );
  }
}
