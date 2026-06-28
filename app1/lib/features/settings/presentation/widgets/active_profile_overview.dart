import 'package:app1/core/themes/app_colors.dart';
import 'package:flutter/material.dart';
import '../../../../app/app_dependencies_scope.dart';
import '../../../authscreen/domain/models/auth_response.dart';
import '../../../authscreen/state/auth_session.dart';
import 'profile_display_helpers.dart';
import 'profile_preview.dart';
import 'settings_components.dart';

class ActiveProfileOverview extends StatelessWidget {
  final AuthSession session;

  const ActiveProfileOverview({super.key, required this.session});

  @override
  Widget build(BuildContext context) {
    if (session.profiles.isEmpty) {
      return const ProfilePreview();
    }

    final activeProfile = session.activeProfile ?? session.profiles.first;

    return SettingsPanel(
      children: [
        ListTile(
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 16,
            vertical: 8,
          ),
          leading: SettingsIconBadge(
            icon: profileIcon(activeProfile.profileType),
            isActive: true,
            large: true,
          ),
          title: Text(
            activeProfile.displayName,
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
          subtitle: Text(profileDescription(activeProfile)),
          trailing: FilledButton.icon(
            onPressed: session.profiles.length < 2
                ? null
                : () => _showProfileSwitcher(context, activeProfile),
            icon: const Icon(Icons.swap_horiz),
            label: const Text('Wechseln'),
            style: FilledButton.styleFrom(
              backgroundColor: AppColors.careenaDark,
              foregroundColor: AppColors.white,
              disabledBackgroundColor: AppColors.careenaBorder,
              disabledForegroundColor: AppColors.careenaMuted,
            ),
          ),
        ),
      ],
    );
  }

  Future<void> _showProfileSwitcher(
    BuildContext context,
    AuthProfile activeProfile,
  ) async {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final selectedProfileId = await showModalBottomSheet<int>(
      context: context,
      backgroundColor: isDark
          ? AppColors.darkElevatedSurface
          : AppColors.careenaNoteBackground,
      isScrollControlled: true,
      showDragHandle: true,
      builder: (context) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
          child: ConstrainedBox(
            constraints: BoxConstraints(
              maxHeight: MediaQuery.sizeOf(context).height * 0.72,
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  'Aktives Profil wechseln',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.w800,
                  ),
                ),
                const SizedBox(height: 12),
                Flexible(
                  // Keeps the sheet usable when many profiles are available.
                  child: SingleChildScrollView(
                    child: SettingsPanel(
                      children: [
                        for (final profile in session.profiles)
                          _ProfileChoiceTile(
                            profile: profile,
                            isActive: profile.id == activeProfile.id,
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

    if (selectedProfileId != null) {
      session.setActiveProfileById(selectedProfileId);
      if (!context.mounted) return;
      await _refreshProfileData(context, selectedProfileId);
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
      // Profile switch should still work even if symptom reload fails.
    }
  }
}

class _ProfileChoiceTile extends StatelessWidget {
  final AuthProfile profile;
  final bool isActive;

  const _ProfileChoiceTile({required this.profile, required this.isActive});

  @override
  Widget build(BuildContext context) {
    return Semantics(
      selected: isActive,
      button: true,
      child: ListTile(
        onTap: () => Navigator.pop(context, profile.id),
        leading: SettingsIconBadge(
          icon: profileIcon(profile.profileType),
          isActive: isActive,
        ),
        title: Text(
          profile.displayName,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Text(profileDescription(profile)),
        trailing: isActive
            ? const Icon(Icons.check_circle, color: AppColors.careenaTeal)
            : null,
      ),
    );
  }
}
