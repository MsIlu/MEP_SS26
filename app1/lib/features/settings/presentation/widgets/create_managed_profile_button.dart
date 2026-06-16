import 'package:flutter/material.dart';

import '../../../../app/app_dependencies_scope.dart';
import '../../../../core/themes/app_colors.dart';
import '../../../authscreen/state/auth_session.dart';
import '../../../profiles/data/profile_api_service.dart';
import 'profile_display_helpers.dart';

class CreateManagedProfileButton extends StatelessWidget {
  final AuthSession? authSession;
  final ProfileApiService? profileApiService;

  const CreateManagedProfileButton({
    super.key,
    required this.authSession,
    required this.profileApiService,
  });

  @override
  Widget build(BuildContext context) {
    return OutlinedButton.icon(
      onPressed: () => _createManagedProfile(context),
      icon: const Icon(Icons.person_add_alt_1),
      label: const Text('Betreutes Profil hinzufügen'),
      style: OutlinedButton.styleFrom(
        foregroundColor: AppColors.careenaTeal,
        side: const BorderSide(color: AppColors.careenaTeal, width: 1.5),
        minimumSize: const Size.fromHeight(56),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      ),
    );
  }

  Future<void> _createManagedProfile(BuildContext context) async {
    final session = authSession;
    final apiService = profileApiService;

    if (session == null || !session.isAuthenticated) {
      _showMessage(context, 'Melde dich an, um ein Profil hinzuzufügen.');
      return;
    }

    if (apiService == null) {
      _showMessage(context, 'Der Profilservice ist aktuell nicht verfügbar.');
      return;
    }

    final draft = await showDialog<_CreateProfileDraft>(
      context: context,
      builder: (context) => const _CreateProfileDialog(),
    );

    if (draft == null || !context.mounted) return;

    try {
      final createdProfile = await apiService.createProfile(
        displayName: draft.displayName,
        profileType: draft.profileType,
      );
      final authProfile = authProfileFromProfile(createdProfile);

      session.setProfiles([...session.profiles, authProfile]);
      session.setActiveProfileById(authProfile.id);
      await _refreshProfileData(context, authProfile.id);

      if (!context.mounted) return;
      _showMessage(
        context,
        'Profil "${authProfile.displayName}" wurde erstellt.',
      );
    } catch (_) {
      if (!context.mounted) return;
      _showMessage(
        context,
        'Das Profil konnte nicht erstellt werden. Bitte versuche es erneut.',
      );
    }
  }

  Future<void> _refreshProfileData(
    BuildContext context,
    int profileId,
  ) async {
    final dependencies = AppDependenciesScope.maybeOf(context);
    if (dependencies == null) {
      return;
    }

    try {
      await dependencies.symptomRepository.clearEntries();
      await dependencies.symptomSyncService.syncActiveProfile(profileId);
    } catch (_) {
      // Keep profile creation flow working even if symptom reload fails.
    }
  }

  void _showMessage(BuildContext context, String message) {
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(SnackBar(content: Text(message)));
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
            'Du bleibst angemeldet und verwaltest Angaben getrennt für diese Person.',
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
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Abbrechen'),
        ),
        FilledButton(
          onPressed: _nameController.text.trim().isEmpty
              ? null
              : () => Navigator.pop(
                  context,
                  _CreateProfileDraft(
                    displayName: _nameController.text.trim(),
                    profileType: profileTypeForRelationship(_relationship),
                  ),
                ),
          child: const Text('Profil speichern'),
        ),
      ],
    );
  }
}

class _CreateProfileDraft {
  final String displayName;
  final String profileType;

  const _CreateProfileDraft({
    required this.displayName,
    required this.profileType,
  });
}