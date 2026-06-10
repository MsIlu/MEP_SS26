import 'package:flutter/material.dart';

import '../../../../core/themes/app_colors.dart';
import '../../../authscreen/domain/models/auth_response.dart';
import '../../../authscreen/state/auth_session.dart';
import '../screens/health_data_settings_page.dart';
import '../screens/personal_data_settings_page.dart';
import 'settings_components.dart';

class ProfileSettingsSection extends StatelessWidget {
  final AuthSession? authSession;

  const ProfileSettingsSection({super.key, required this.authSession});

  @override
  Widget build(BuildContext context) {
    final session = authSession;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const SettingsSectionHeader(
          icon: Icons.people_outline,
          title: 'Profile verwalten',
          subtitle: 'Wähle aus, für wen du die App verwendest.',
        ),
        const SizedBox(height: 10),
        if (session == null)
          const _ProfilePreview()
        else
          AnimatedBuilder(
            animation: session,
            builder: (context, _) => _ProfileList(session: session),
          ),
        const SizedBox(height: 10),
        SettingsPanel(
          children: [
            SettingsLinkTile(
              icon: Icons.badge_outlined,
              title: 'Persönliche Daten',
              description: 'Name, Geburtsdatum und Kontodaten',
              page: PersonalDataSettingsPage(authSession: session),
            ),
            SettingsLinkTile(
              icon: Icons.health_and_safety_outlined,
              title: 'Gesundheitsangaben',
              description: 'Körperdaten und medizinische Hinweise',
              page: HealthDataSettingsPage(authSession: session),
            ),
          ],
        ),
        const SizedBox(height: 10),
        OutlinedButton.icon(
          onPressed: () => _showCreateProfileDialog(context),
          icon: const Icon(Icons.person_add_alt_1),
          label: const Text('Betreutes Profil hinzufügen'),
          style: OutlinedButton.styleFrom(
            foregroundColor: AppColors.careenaTeal,
            side: const BorderSide(color: AppColors.careenaTeal, width: 1.5),
            minimumSize: const Size.fromHeight(56),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(20),
            ),
          ),
        ),
      ],
    );
  }

  Future<void> _showCreateProfileDialog(BuildContext context) async {
    final submitted = await showDialog<bool>(
      context: context,
      builder: (context) => const _CreateProfileDialog(),
    );

    if (submitted != true || !context.mounted) return;

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text(
          'Das Profil wurde als Entwurf erfasst. Die Speicherung folgt mit der Profilanbindung.',
        ),
      ),
    );
  }
}

class _ProfileList extends StatelessWidget {
  final AuthSession session;

  const _ProfileList({required this.session});

  @override
  Widget build(BuildContext context) {
    if (session.profiles.isEmpty) {
      return const _ProfilePreview();
    }

    return SettingsPanel(
      children: [
        for (final profile in session.profiles)
          _ProfileTile(
            profile: profile,
            isActive: session.activeProfileId == profile.id,
            onTap: () => session.setActiveProfileById(profile.id),
          ),
      ],
    );
  }
}

class _ProfileTile extends StatelessWidget {
  final AuthProfile profile;
  final bool isActive;
  final VoidCallback onTap;

  const _ProfileTile({
    required this.profile,
    required this.isActive,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Semantics(
      selected: isActive,
      button: true,
      child: ListTile(
        onTap: onTap,
        leading: SettingsIconBadge(
          icon: _profileIcon(profile.profileType),
          isActive: isActive,
        ),
        title: Text(
          profile.displayName,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Text(_profileDescription(profile)),
        trailing: Icon(
          isActive ? Icons.check_circle : Icons.radio_button_unchecked,
          color: AppColors.careenaTeal,
        ),
      ),
    );
  }
}

class _ProfilePreview extends StatelessWidget {
  const _ProfilePreview();

  @override
  Widget build(BuildContext context) {
    return const SettingsPanel(
      children: [
        ListTile(
          leading: SettingsIconBadge(icon: Icons.person_outline),
          title: Text(
            'Eigenes Profil',
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
          subtitle: Text('Nach der Anmeldung hier auswählbar'),
        ),
        ListTile(
          leading: SettingsIconBadge(icon: Icons.child_care),
          title: Text(
            'Betreutes Profil',
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
          subtitle: Text('Zum Beispiel für ein minderjähriges Kind'),
        ),
      ],
    );
  }
}

class _CreateProfileDialog extends StatefulWidget {
  const _CreateProfileDialog();

  @override
  State<_CreateProfileDialog> createState() => _CreateProfileDialogState();
}

class _CreateProfileDialogState extends State<_CreateProfileDialog> {
  final _nameController = TextEditingController();
  String _relationship = 'Kind';

  @override
  void dispose() {
    _nameController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      icon: const Icon(Icons.person_add_alt_1, size: 36),
      title: const Text('Betreutes Profil hinzufügen'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const Text(
            'Du bleibst angemeldet und kannst Angaben getrennt für diese Person verwalten.',
          ),
          const SizedBox(height: 18),
          TextField(
            controller: _nameController,
            autofocus: true,
            decoration: const InputDecoration(
              labelText: 'Name der betreuten Person',
              prefixIcon: Icon(Icons.person_outline),
            ),
            onChanged: (_) => setState(() {}),
          ),
          const SizedBox(height: 14),
          DropdownButtonFormField<String>(
            initialValue: _relationship,
            decoration: const InputDecoration(
              labelText: 'Beziehung',
              prefixIcon: Icon(Icons.family_restroom),
            ),
            items: const [
              DropdownMenuItem(value: 'Kind', child: Text('Kind')),
              DropdownMenuItem(
                value: 'Familienmitglied',
                child: Text('Familienmitglied'),
              ),
              DropdownMenuItem(
                value: 'Andere Person',
                child: Text('Andere betreute Person'),
              ),
            ],
            onChanged: (value) {
              if (value != null) setState(() => _relationship = value);
            },
          ),
          const SizedBox(height: 14),
          const Text(
            'Hinweis: Dieses Formular ist aktuell eine Frontend-Vorschau.',
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context, false),
          child: const Text('Abbrechen'),
        ),
        FilledButton(
          onPressed: _nameController.text.trim().isEmpty
              ? null
              : () => Navigator.pop(context, true),
          child: const Text('Entwurf übernehmen'),
        ),
      ],
    );
  }
}

IconData _profileIcon(String profileType) => switch (profileType) {
  'child' => Icons.child_care,
  'self' => Icons.person_outline,
  _ => Icons.people_outline,
};

String _profileDescription(AuthProfile profile) {
  if (profile.profileType == 'child') {
    return 'Betreutes Profil';
  }

  if (profile.profileType == 'self') {
    return 'Eigenes Profil';
  }

  return profile.role == null ? 'Weiteres Profil' : 'Rolle: ${profile.role}';
}
