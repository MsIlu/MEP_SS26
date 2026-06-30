import 'package:app1/app/app_dependencies_scope.dart';
import 'package:app1/core/themes/app_colors.dart';
import 'package:app1/core/widgets/careena_snack_bar.dart';
import 'package:flutter/material.dart';

import '../../../authscreen/domain/models/auth_response.dart';
import '../../../authscreen/state/auth_session.dart';
import '../../../profiles/data/profile_api_service.dart';
import '../screens/profile_data_settings_page.dart';
import '../settings_icons.dart';
import 'active_profile_overview.dart';
import 'create_managed_profile_button.dart';
import 'profile_preview.dart';
import 'profile_display_helpers.dart';
import 'settings_components.dart';

class ProfileSettingsSection extends StatelessWidget {
  final AuthSession? authSession;
  final ProfileApiService? profileApiService;

  const ProfileSettingsSection({
    super.key,
    required this.authSession,
    this.profileApiService,
  });

  @override
  Widget build(BuildContext context) {
    final session = authSession;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const SettingsSectionHeader(
          icon: SettingsIcons.profiles,
          title: 'Profile verwalten',
          subtitle: 'Wähle aus, für wen du Careena gerade nutzt.',
        ),
        const SizedBox(height: 10),
        if (session == null)
          const ProfilePreview()
        else
          AnimatedBuilder(
            animation: session,
            builder: (context, _) => ActiveProfileOverview(session: session),
          ),
        const SizedBox(height: 12),
        SettingsPrimaryButton(
          icon: Icons.edit_note,
          label: 'Profildaten bearbeiten',
          onPressed: session?.activeProfile == null
              ? null
              : () => Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => ProfileDataSettingsPage(
                      authSession: session,
                      profileApiService: profileApiService,
                    ),
                  ),
                ),
        ),
        const SizedBox(height: 10),
        CreateManagedProfileButton(
          authSession: session,
          profileApiService: profileApiService,
        ),
        if (session != null)
          AnimatedBuilder(
            animation: session,
            builder: (context, _) {
              if (_deletableProfiles(session).isEmpty ||
                  profileApiService == null) {
                return const SizedBox.shrink();
              }

              return Padding(
                padding: const EdgeInsets.only(top: 12),
                child: OutlinedButton.icon(
                  key: const ValueKey('settings-delete-profile-button'),
                  onPressed: () => _selectProfileToDelete(context),
                  icon: const Icon(Icons.person_remove_outlined),
                  label: const Text('Profil löschen'),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: AppColors.warningRed,
                    side: const BorderSide(color: AppColors.warningRed),
                    minimumSize: const Size.fromHeight(52),
                  ),
                ),
              );
            },
          ),
      ],
    );
  }

  List<AuthProfile> _deletableProfiles(AuthSession session) {
    if (!session.isAuthenticated) return const [];
    return session.profiles
        .where(
          (profile) =>
              profile.profileType != 'self' &&
              (profile.role == 'owner' ||
                  profile.role == 'guardian' ||
                  (profile.role == 'editor' &&
                      const {'child', 'relative', 'family', 'other'}.contains(
                        profile.profileType,
                      ))),
        )
        .toList();
  }

  Future<void> _selectProfileToDelete(BuildContext context) async {
    final session = authSession!;
    final profiles = _deletableProfiles(session);
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final profile = await showModalBottomSheet<AuthProfile>(
      context: context,
      backgroundColor: isDark
          ? AppColors.darkElevatedSurface
          : AppColors.careenaNoteBackground,
      isScrollControlled: true,
      showDragHandle: true,
      builder: (sheetContext) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
          child: ConstrainedBox(
            constraints: BoxConstraints(
              maxHeight: MediaQuery.sizeOf(sheetContext).height * 0.72,
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  'Profil löschen',
                  style: Theme.of(
                    sheetContext,
                  ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800),
                ),
                const SizedBox(height: 12),
                Flexible(
                  child: SingleChildScrollView(
                    child: SettingsPanel(
                      children: [
                        for (final profile in profiles)
                          ListTile(
                            onTap: () => Navigator.pop(sheetContext, profile),
                            leading: SettingsIconBadge(
                              icon: profileIcon(profile.profileType),
                              isActive: false,
                            ),
                            title: Text(
                              profile.displayName,
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            subtitle: Text(profileDescription(profile)),
                            trailing: const Icon(Icons.chevron_right),
                          ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );

    if (profile == null || !context.mounted) return;
    await _confirmProfileDeletion(context, profile);
  }

  Future<void> _confirmProfileDeletion(
    BuildContext context,
    AuthProfile profile,
  ) async {
    final session = authSession!;
    final apiService = profileApiService!;
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (dialogContext) {
        final isDark = Theme.of(dialogContext).brightness == Brightness.dark;
        return AlertDialog(
          backgroundColor: isDark
              ? AppColors.warningEmergencyBackgroundDark
              : AppColors.warningBackground,
          title: Row(
            children: [
              const Icon(
                Icons.warning_amber_rounded,
                color: AppColors.warningRed,
                size: 30,
              ),
              const SizedBox(width: 12),
              Expanded(child: Text('Profil "${profile.displayName}" löschen?')),
            ],
          ),
          content: const Text(
            'Das Profil und seine Gesundheitsdaten werden deaktiviert und '
            'nicht mehr in Careena angezeigt.',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(dialogContext, false),
              child: const Text('Abbrechen'),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(dialogContext, true),
              style: FilledButton.styleFrom(
                backgroundColor: AppColors.warningRed,
                foregroundColor: AppColors.white,
              ),
              child: const Text('Profil löschen'),
            ),
          ],
        );
      },
    );

    if (confirmed != true || !context.mounted) return;

    try {
      await apiService.deleteProfile(profile.id);
      final remainingProfiles = await apiService.getProfiles();
      session.setProfiles(
        remainingProfiles.map(authProfileFromProfile).toList(),
      );

      if (!context.mounted) return;

      final dependencies = AppDependenciesScope.maybeOf(context);
      if (dependencies != null) {
        try {
          await dependencies.symptomRepository.clearEntries();
          final nextProfileId = session.activeProfileId;
          if (nextProfileId != null) {
            await dependencies.symptomSyncService.syncActiveProfile(
              nextProfileId,
            );
          }
        } catch (_) {
          // The backend deletion succeeded even if local symptom refresh fails.
        }
      }

      if (!context.mounted) return;
      showCareenaSnackBar(context, 'Das Profil wurde gelöscht.');
    } catch (_) {
      if (!context.mounted) return;
      showCareenaSnackBar(
        context,
        'Das Profil konnte nicht gelöscht werden. Bitte versuche es erneut.',
      );
    }
  }
}
