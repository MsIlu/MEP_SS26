import 'package:app1/app/app_dependencies_scope.dart';
import 'package:app1/core/themes/app_colors.dart';
import 'package:app1/features/authscreen/domain/models/auth_response.dart';
import 'package:app1/features/authscreen/state/auth_session.dart';
import 'package:flutter/material.dart';

class ActiveProfileHeaderAction extends StatelessWidget {
  final AuthSession? session;

  const ActiveProfileHeaderAction({super.key, this.session});

  static bool hasActiveProfile(BuildContext context) {
    return AppDependenciesScope.maybeOf(context)?.authSession.activeProfile !=
        null;
  }

  @override
  Widget build(BuildContext context) {
    final activeSession =
        session ?? AppDependenciesScope.maybeOf(context)?.authSession;

    if (activeSession == null) {
      return const SizedBox.square(dimension: 48);
    }

    return AnimatedBuilder(
      animation: activeSession,
      builder: (context, _) => _buildProfileAction(context, activeSession),
    );
  }

  Widget _buildProfileAction(BuildContext context, AuthSession activeSession) {
    final activeProfile = activeSession.activeProfile;

    if (activeProfile == null) {
      return const SizedBox.square(dimension: 48);
    }

    final isDark = Theme.of(context).brightness == Brightness.dark;
    final screenWidth = MediaQuery.sizeOf(context).width;
    final isNarrow = screenWidth < 390;
    final maxWidth = screenWidth >= 700 ? 220.0 : (isNarrow ? 92.0 : 144.0);
    final label = isNarrow
        ? _firstName(activeProfile.displayName)
        : activeProfile.displayName;

    return Tooltip(
      message: 'Aktives Profil: ${activeProfile.displayName}',
      child: InkWell(
        borderRadius: BorderRadius.circular(24),
        onTap: activeSession.profiles.length < 2
            ? null
            : () => _showProfileSwitcher(context, activeSession, activeProfile),
        child: Container(
          height: 42,
          constraints: BoxConstraints(maxWidth: maxWidth),
          padding: const EdgeInsets.symmetric(horizontal: 9),
          decoration: BoxDecoration(
            color: isDark
                ? AppColors.toolbarButtonBackgroundDark
                : AppColors.toolbarButtonBackground,
            borderRadius: BorderRadius.circular(24),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                _profileIcon(activeProfile.profileType),
                size: 18,
                color: isDark
                    ? AppColors.toolbarButtonForegroundDark
                    : AppColors.toolbarButtonForeground,
              ),
              const SizedBox(width: 6),
              Flexible(
                child: Text(
                  label,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(
                    color: isDark
                        ? AppColors.toolbarButtonForegroundDark
                        : AppColors.toolbarButtonForeground,
                    fontSize: 12,
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ),
              if (activeSession.profiles.length > 1) ...[
                const SizedBox(width: 4),
                Icon(
                  Icons.keyboard_arrow_down,
                  size: 16,
                  color: isDark
                      ? AppColors.toolbarButtonForegroundDark
                      : AppColors.toolbarButtonForeground,
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _showProfileSwitcher(
    BuildContext context,
    AuthSession session,
    AuthProfile activeProfile,
  ) async {
    final selectedProfileId = await showModalBottomSheet<int>(
      context: context,
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
                  style: Theme.of(
                    context,
                  ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800),
                ),
                const SizedBox(height: 12),
                Flexible(
                  child: ListView.builder(
                    shrinkWrap: true,
                    itemCount: session.profiles.length,
                    itemBuilder: (context, index) {
                      final profile = session.profiles[index];

                      return _ProfileSwitchTile(
                        profile: profile,
                        isActive: profile.id == activeProfile.id,
                      );
                    },
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );

    if (selectedProfileId == null) return;

    session.setActiveProfileById(selectedProfileId);
    if (!context.mounted) return;
    await _refreshProfileData(context, selectedProfileId);
  }

  Future<void> _refreshProfileData(BuildContext context, int profileId) async {
    final dependencies = AppDependenciesScope.maybeOf(context);
    if (dependencies == null) return;

    try {
      await dependencies.symptomRepository.clearEntries();
      await dependencies.symptomSyncService.syncActiveProfile(profileId);
    } catch (_) {
      // Profile switching should not fail just because cached diary data cannot refresh.
    }
  }
}

class _ProfileSwitchTile extends StatelessWidget {
  final AuthProfile profile;
  final bool isActive;

  const _ProfileSwitchTile({required this.profile, required this.isActive});

  @override
  Widget build(BuildContext context) {
    return ListTile(
      onTap: () => Navigator.pop(context, profile.id),
      leading: Icon(_profileIcon(profile.profileType)),
      title: Text(
        profile.displayName,
        style: const TextStyle(fontWeight: FontWeight.bold),
      ),
      subtitle: Text(_profileDescription(profile)),
      trailing: isActive
          ? const Icon(Icons.check_circle, color: AppColors.careenaTeal)
          : null,
    );
  }
}

String _firstName(String displayName) {
  final trimmedName = displayName.trim();
  if (trimmedName.isEmpty) return displayName;

  return trimmedName.split(RegExp(r'\s+')).first;
}

IconData _profileIcon(String profileType) => switch (profileType) {
  'child' => Icons.child_care,
  'self' => Icons.person_outline,
  _ => Icons.people_outline,
};

String _profileDescription(AuthProfile profile) {
  return switch (profile.profileType) {
    'child' => 'Kind',
    'family' => 'Familienmitglied',
    'other' => 'Andere betreute Person',
    'self' => 'Eigenes Profil',
    _ => 'Betreutes Profil',
  };
}
