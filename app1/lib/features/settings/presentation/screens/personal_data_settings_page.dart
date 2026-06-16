import 'package:flutter/material.dart';

import '../../../authscreen/presentation/widgets/common/auth_fields.dart';
import '../../../authscreen/presentation/widgets/registration/birth_date/birth_date_field_with_age.dart';
import '../../../authscreen/state/auth_session.dart';
import '../../../authscreen/utils/auth_validators.dart';
import '../../../authscreen/utils/birth_date_utils.dart';
import '../../../profiles/data/profile_api_service.dart';
import '../settings_icons.dart';
import '../widgets/settings_components.dart';
import '../widgets/settings_detail_scaffold.dart';

class PersonalDataSettingsPage extends StatelessWidget {
  final AuthSession? authSession;
  final ProfileApiService? profileApiService;

  const PersonalDataSettingsPage({
    super.key,
    required this.authSession,
    this.profileApiService,
  });

  @override
  Widget build(BuildContext context) {
    return SettingsDetailScaffold(
      title: 'Persönliche Daten',
      subtitle: 'Daten des aktuell ausgewählten Profils.',
      icon: SettingsIcons.personalData,
      child: PersonalDataSettingsForm(
        authSession: authSession,
        profileApiService: profileApiService,
      ),
    );
  }
}

class PersonalDataSettingsForm extends StatefulWidget {
  final AuthSession? authSession;
  final ProfileApiService? profileApiService;

  const PersonalDataSettingsForm({
    super.key,
    required this.authSession,
    this.profileApiService,
  });

  @override
  State<PersonalDataSettingsForm> createState() =>
      _PersonalDataSettingsFormState();
}

class _PersonalDataSettingsFormState extends State<PersonalDataSettingsForm> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _nameController;
  final _birthDateController = TextEditingController();
  final _birthDayController = TextEditingController();
  final _birthMonthController = TextEditingController();
  final _birthYearController = TextEditingController();
  final _ageController = TextEditingController();
  final _birthDayFocusNode = FocusNode();
  final _birthMonthFocusNode = FocusNode();
  final _birthYearFocusNode = FocusNode();

  @override
  void initState() {
    super.initState();
    _nameController = TextEditingController(
      text: widget.authSession?.activeProfile?.displayName ?? '',
    );
    _birthDateController.addListener(_refreshAge);
    _loadProfileBirthDate();
  }

  @override
  void dispose() {
    _birthDateController.removeListener(_refreshAge);
    _nameController.dispose();
    _birthDateController.dispose();
    _birthDayController.dispose();
    _birthMonthController.dispose();
    _birthYearController.dispose();
    _ageController.dispose();
    _birthDayFocusNode.dispose();
    _birthMonthFocusNode.dispose();
    _birthYearFocusNode.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final session = widget.authSession;
    final profileType = session?.activeProfile?.profileType == 'child'
        ? 'Betreutes Profil'
        : 'Eigenes Profil';

    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          AuthTextField(
            controller: _nameController,
            label: 'Anzeigename',
            hint: 'Vor- und Nachname',
            validator: AuthValidators.requiredText,
          ),
          const SizedBox(height: 14),
          BirthDateFieldWithAge(
            dayController: _birthDayController,
            monthController: _birthMonthController,
            yearController: _birthYearController,
            ageController: _ageController,
            dayFocusNode: _birthDayFocusNode,
            monthFocusNode: _birthMonthFocusNode,
            yearFocusNode: _birthYearFocusNode,
            birthDateController: _birthDateController,
            showValidation: _isBirthDateComplete,
            onChanged: _syncBirthDate,
          ),
          const SizedBox(height: 14),
          _ReadOnlyDataTile(
            icon: Icons.person_outline,
            label: 'Profilart',
            value: profileType,
          ),
          const SizedBox(height: 10),
          _ReadOnlyDataTile(
            icon: Icons.email_outlined,
            label: 'E-Mail des angemeldeten Kontos',
            value: session?.account?.email ?? 'Nach Anmeldung verfügbar',
          ),
          const SizedBox(height: 18),
          SettingsPrimaryButton(
            key: const ValueKey('personal-data-save-button'),
            onPressed: _saveDraft,
            icon: Icons.save_outlined,
            label: 'Änderungen übernehmen',
          ),
        ],
      ),
    );
  }

  void _saveDraft() {
    if (!(_formKey.currentState?.validate() ?? false)) return;
    _saveProfile();
  }

  Future<void> _saveProfile() async {
    final profileId = widget.authSession?.activeProfileId;
    final profileApiService = widget.profileApiService;

    if (profileId == null || profileApiService == null) {
      _showMessage('Der Profilservice ist aktuell nicht verfügbar.');
      return;
    }

    try {
      final displayName = _nameController.text.trim();
      await profileApiService.updateProfileFields(
        profileId: profileId,
        fields: {
          'display_name': displayName,
          'date_of_birth': _dateOfBirthForBackend(),
        },
      );
      widget.authSession?.setActiveProfileDisplayName(displayName);

      if (!mounted) return;
      _showMessage('Persönliche Angaben wurden gespeichert.');
    } catch (_) {
      if (!mounted) return;
      _showMessage(
        'Persönliche Angaben konnten nicht gespeichert werden. Bitte versuche es erneut.',
      );
    }
  }

  Future<void> _loadProfileBirthDate() async {
    final profileId = widget.authSession?.activeProfileId;
    final profileApiService = widget.profileApiService;

    if (profileId == null || profileApiService == null) {
      return;
    }

    try {
      final profile = await profileApiService.getProfile(profileId);
      final dateOfBirth = profile.dateOfBirth;

      if (!mounted || dateOfBirth == null) {
        return;
      }

      _setBirthDate(dateOfBirth);
    } catch (_) {
      return;
    }
  }

  void _setBirthDate(String isoDate) {
    final parts = isoDate.split('-');

    if (parts.length != 3) {
      return;
    }

    _birthYearController.text = parts[0];
    _birthMonthController.text = parts[1];
    _birthDayController.text = parts[2];
    _birthDateController.text = '${parts[2]}.${parts[1]}.${parts[0]}';
  }

  void _refreshAge() {
    if (!mounted) return;

    final age = BirthDateUtils.calculateAge(_birthDateController.text);
    _ageController.text = age == null ? '' : _formatAge(age);
    setState(() {});
  }

  String _formatAge(int age) {
    return age == 1 ? '1 Jahr' : '$age Jahre';
  }

  void _syncBirthDate() {
    _birthDateController.text =
        '${_birthDayController.text}.${_birthMonthController.text}.${_birthYearController.text}';
  }

  String? _dateOfBirthForBackend() {
    if (!_isBirthDateComplete) return null;
    return '${_birthYearController.text}-${_birthMonthController.text}-${_birthDayController.text}';
  }

  void _showMessage(String message) {
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(SnackBar(content: Text(message)));
  }

  bool get _isBirthDateComplete {
    return _birthDayController.text.length == 2 &&
        _birthMonthController.text.length == 2 &&
        _birthYearController.text.length == 4;
  }
}

class _ReadOnlyDataTile extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;

  const _ReadOnlyDataTile({
    required this.icon,
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: Icon(icon),
      title: Text(label),
      subtitle: Text(value),
      trailing: const Icon(Icons.lock_outline),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(18),
        side: BorderSide(color: Theme.of(context).colorScheme.outlineVariant),
      ),
    );
  }
}
