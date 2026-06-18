import 'package:flutter/material.dart';

import '../../../../core/themes/app_colors.dart';
import '../../../authscreen/data/registration_condition_options.dart';
import '../../../authscreen/presentation/widgets/common/auth_fields.dart';
import '../../../authscreen/state/auth_session.dart';
import '../../../authscreen/utils/auth_validators.dart';
import '../../../profiles/data/profile_api_service.dart';
import '../settings_icons.dart';
import '../widgets/settings_components.dart';
import '../widgets/settings_detail_scaffold.dart';

class HealthDataSettingsPage extends StatelessWidget {
  final AuthSession? authSession;
  final ProfileApiService? profileApiService;

  const HealthDataSettingsPage({
    super.key,
    required this.authSession,
    this.profileApiService,
  });

  @override
  Widget build(BuildContext context) {
    final session = authSession;

    if (session != null) {
      return AnimatedBuilder(
        animation: session,
        builder: (context, _) => _buildContent(context),
      );
    }

    return _buildContent(context);
  }

  Widget _buildContent(BuildContext context) {
    final profileName =
        authSession?.activeProfile?.displayName ?? 'dieses Profil';
    final activeProfileId = authSession?.activeProfileId;

    return SettingsDetailScaffold(
      title: 'Gesundheitsangaben',
      subtitle: 'Medizinischer Kontext für $profileName.',
      icon: SettingsIcons.healthData,
      child: HealthDataSettingsForm(
        key: ValueKey('health-data-page-$activeProfileId'),
        authSession: authSession,
        profileApiService: profileApiService,
      ),
    );
  }
}

class HealthDataSettingsForm extends StatefulWidget {
  final AuthSession? authSession;
  final ProfileApiService? profileApiService;

  const HealthDataSettingsForm({
    super.key,
    required this.authSession,
    this.profileApiService,
  });

  @override
  State<HealthDataSettingsForm> createState() => _HealthDataSettingsFormState();
}

class _HealthDataSettingsFormState extends State<HealthDataSettingsForm> {
  final _formKey = GlobalKey<FormState>();
  final _heightController = TextEditingController();
  final _weightController = TextEditingController();
  final _medicationController = TextEditingController();
  final _notesController = TextEditingController();
  final _conditions = <String>{};
  String _biologicalSex = 'Keine Angabe';

  @override
  void initState() {
    super.initState();
    _loadProfile();
  }

  @override
  void dispose() {
    _heightController.dispose();
    _weightController.dispose();
    _medicationController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          DropdownButtonFormField<String>(
            initialValue: _biologicalSex,
            decoration: const InputDecoration(
              labelText: 'Geburtsgeschlecht',
              prefixIcon: Icon(Icons.wc_outlined),
            ),
            items: const [
              DropdownMenuItem(
                value: 'Keine Angabe',
                child: Text('Keine Angabe'),
              ),
              DropdownMenuItem(value: 'Weiblich', child: Text('Weiblich')),
              DropdownMenuItem(value: 'Männlich', child: Text('Männlich')),
            ],
            onChanged: (value) {
              if (value != null) setState(() => _biologicalSex = value);
            },
          ),
          const SizedBox(height: 14),
          AuthTextField(
            controller: _heightController,
            label: 'Größe',
            hint: 'z. B. 170',
            suffixText: 'cm',
            keyboardType: TextInputType.number,
            validator: _optionalHeight,
          ),
          const SizedBox(height: 14),
          AuthTextField(
            controller: _weightController,
            label: 'Gewicht',
            hint: 'z. B. 70,5',
            suffixText: 'kg',
            keyboardType: const TextInputType.numberWithOptions(decimal: true),
            validator: _optionalWeight,
          ),
          const SizedBox(height: 20),
          Text(
            'Vorerkrankungen',
            style: Theme.of(
              context,
            ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              for (final condition in registrationConditionOptions)
                FilterChip(
                  label: Text(condition),
                  selected: _conditions.contains(condition),
                  selectedColor: AppColors.careenaSoftAccent,
                  checkmarkColor: AppColors.careenaDark,
                  backgroundColor:
                      Theme.of(context).brightness == Brightness.dark
                      ? AppColors.darkMutedSurface
                      : AppColors.careenaNoteBackground,
                  side: BorderSide(
                    color: _conditions.contains(condition)
                        ? AppColors.careenaPrimary
                        : AppColors.careenaBorder,
                  ),
                  labelStyle: TextStyle(
                    color: _conditions.contains(condition)
                        ? AppColors.careenaDark
                        : null,
                    fontWeight: _conditions.contains(condition)
                        ? FontWeight.w700
                        : FontWeight.w500,
                  ),
                  onSelected: (selected) => setState(() {
                    selected
                        ? _conditions.add(condition)
                        : _conditions.remove(condition);
                  }),
                ),
            ],
          ),
          const SizedBox(height: 20),
          AuthTextField(
            controller: _medicationController,
            label: 'Regelmäßige Medikamente',
            hint: 'Optional',
            maxLines: 3,
          ),
          const SizedBox(height: 14),
          AuthTextField(
            controller: _notesController,
            label: 'Symptomtagebuch-Zusammenfassung',
            hint: 'Optional',
            maxLines: 4,
          ),
          const SizedBox(height: 18),
          SettingsPrimaryButton(
            key: const ValueKey('health-data-save-button'),
            onPressed: _saveDraft,
            icon: Icons.save_outlined,
            label: 'Änderungen übernehmen',
          ),
        ],
      ),
    );
  }

  String? _optionalHeight(String? value) {
    if ((value ?? '').trim().isEmpty) return null;
    return AuthValidators.heightCm(value);
  }

  String? _optionalWeight(String? value) {
    if ((value ?? '').trim().isEmpty) return null;
    return AuthValidators.weightKg(value);
  }

  void _saveDraft() {
    if (!(_formKey.currentState?.validate() ?? false)) return;
    _saveProfile();
  }

  Future<void> _loadProfile() async {
    final profileId = widget.authSession?.activeProfileId;
    final profileApiService = widget.profileApiService;

    if (profileId == null || profileApiService == null) {
      return;
    }

    try {
      final profile = await profileApiService.getProfile(profileId);

      if (!mounted) return;

      setState(() {
        _biologicalSex = _sexLabelFromBackend(profile.biologicalSex);
        _heightController.text = profile.heightCm?.toString() ?? '';
        _weightController.text = _formatWeight(profile.weightKg);
        _medicationController.text = profile.relevantMedicationsSummary ?? '';
        _notesController.text = profile.symptomDiarySummary ?? '';
        _conditions
          ..clear()
          ..addAll(
            _conditionsFromSummary(profile.relevantPreconditionsSummary),
          );
      });
    } catch (_) {
      return;
    }
  }

  Future<void> _saveProfile() async {
    final profileId = widget.authSession?.activeProfileId;
    final profileApiService = widget.profileApiService;

    if (profileId == null || profileApiService == null) {
      _showMessage('Der Profilservice ist aktuell nicht verfügbar.');
      return;
    }

    try {
      await profileApiService.updateProfileFields(
        profileId: profileId,
        fields: {
          'biological_sex': _sexValueForBackend(_biologicalSex),
          'height_cm': int.tryParse(_heightController.text.trim()),
          'weight_kg': double.tryParse(
            _weightController.text.trim().replaceAll(',', '.'),
          ),
          'relevant_preconditions_summary': _summaryFromConditions(),
          'relevant_medications_summary': _emptyToNull(
            _medicationController.text,
          ),
          'symptom_diary_summary': _emptyToNull(_notesController.text),
        },
      );

      if (!mounted) return;
      _showMessage('Gesundheitsangaben wurden gespeichert.');
    } catch (_) {
      if (!mounted) return;
      _showMessage(
        'Gesundheitsangaben konnten nicht gespeichert werden. Bitte versuche es erneut.',
      );
    }
  }

  List<String> _conditionsFromSummary(String? summary) {
    if (summary == null || summary.trim().isEmpty) return [];
    return summary
        .split(',')
        .map((item) => item.trim())
        .where((item) => item.isNotEmpty)
        .toList();
  }

  String? _summaryFromConditions() {
    if (_conditions.isEmpty) return null;
    return _conditions.join(', ');
  }

  String _formatWeight(double? value) {
    if (value == null) return '';
    return value.toString().replaceAll('.', ',');
  }

  String _sexLabelFromBackend(String? value) {
    return switch (value) {
      'female' => 'Weiblich',
      'male' => 'Männlich',
      _ => 'Keine Angabe',
    };
  }

  String? _sexValueForBackend(String value) {
    return switch (value) {
      'Weiblich' => 'female',
      'Männlich' => 'male',
      _ => null,
    };
  }

  String? _emptyToNull(String value) {
    final trimmed = value.trim();
    return trimmed.isEmpty ? null : trimmed;
  }

  void _showMessage(String message) {
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(SnackBar(content: Text(message)));
  }
}