import 'package:flutter/material.dart';

import '../../../authscreen/state/auth_session.dart';
import '../../../authscreen/utils/auth_validators.dart';
import '../../../authscreen/presentation/widgets/common/auth_fields.dart';
import '../settings_icons.dart';
import '../widgets/settings_detail_scaffold.dart';
import '../widgets/settings_components.dart';

class PersonalDataSettingsPage extends StatefulWidget {
  final AuthSession? authSession;

  const PersonalDataSettingsPage({super.key, required this.authSession});

  @override
  State<PersonalDataSettingsPage> createState() =>
      _PersonalDataSettingsPageState();
}

class _PersonalDataSettingsPageState extends State<PersonalDataSettingsPage> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _nameController;
  final _birthDateController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _nameController = TextEditingController(
      text: widget.authSession?.activeProfile?.displayName ?? '',
    );
  }

  @override
  void dispose() {
    _nameController.dispose();
    _birthDateController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final session = widget.authSession;
    final profileType = session?.activeProfile?.profileType == 'child'
        ? 'Betreutes Profil'
        : 'Eigenes Profil';

    return SettingsDetailScaffold(
      title: 'Persönliche Daten',
      subtitle: 'Daten des aktuell ausgewählten Profils.',
      icon: SettingsIcons.personalData,
      child: Form(
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
            AuthTextField(
              controller: _birthDateController,
              label: 'Geburtsdatum',
              hint: 'TT.MM.JJJJ',
              keyboardType: TextInputType.datetime,
              validator: _optionalBirthDate,
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
            const SettingsDraftNotice(),
            const SizedBox(height: 18),
            SettingsPrimaryButton(
              key: const ValueKey('settings-save-button'),
              onPressed: _saveDraft,
              icon: Icons.save_outlined,
              label: 'Änderungen übernehmen',
            ),
          ],
        ),
      ),
    );
  }

  void _saveDraft() {
    if (!(_formKey.currentState?.validate() ?? false)) return;
    showDraftSavedMessage(context);
  }

  String? _optionalBirthDate(String? value) {
    if ((value ?? '').trim().isEmpty) return null;
    return AuthValidators.birthDate(value);
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
