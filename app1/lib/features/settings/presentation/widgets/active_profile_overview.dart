import 'package:app1/core/themes/app_colors.dart';
import 'package:app1/core/widgets/simple_view.dart';
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
        _ActiveProfileTile(
          profile: activeProfile,
          canSwitchProfile: session.profiles.length >= 2,
          onSwitchProfile: () => _showProfileSwitcher(context, activeProfile),
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
                  style: Theme.of(
                    context,
                  ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800),
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

  Future<void> _refreshProfileData(BuildContext context, int profileId) async {
    final dependencies = AppDependenciesScope.maybeOf(context);
    if (dependencies == null) {
      return;
    }

    try {
      await dependencies.symptomSyncService.syncActiveProfile(profileId);
    } catch (_) {
      // Profile switch should still work even if symptom reload fails.
    }
  }
}

class _ActiveProfileTile extends StatelessWidget {
  final AuthProfile profile;
  final bool canSwitchProfile;
  final VoidCallback onSwitchProfile;

  const _ActiveProfileTile({
    required this.profile,
    required this.canSwitchProfile,
    required this.onSwitchProfile,
  });

  @override
  Widget build(BuildContext context) {
    final simpleView = SimpleViewScope.isEnabled(context);
    final switchButton = _SwitchProfileButton(
      enabled: canSwitchProfile,
      onPressed: onSwitchProfile,
    );

    return LayoutBuilder(
      builder: (context, constraints) {
        final compactLayout = simpleView || constraints.maxWidth < 520;

        if (compactLayout) {
          return Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    SettingsIconBadge(
                      icon: profileIcon(profile.profileType),
                      isActive: true,
                      large: true,
                    ),
                    const SizedBox(width: 14),
                    Expanded(child: _ProfileText(profile: profile)),
                  ],
                ),
                const SizedBox(height: 14),
                switchButton,
              ],
            ),
          );
        }

        return ListTile(
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 16,
            vertical: 8,
          ),
          leading: SettingsIconBadge(
            icon: profileIcon(profile.profileType),
            isActive: true,
            large: true,
          ),
          title: _ProfileText(profile: profile, titleOnly: true),
          subtitle: Text(profileDescription(profile)),
          // Keep the action bounded so Material ListTile never receives a
          // trailing control that consumes the whole tile width.
          trailing: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 160),
            child: switchButton,
          ),
        );
      },
    );
  }
}

class _ProfileText extends StatelessWidget {
  final AuthProfile profile;
  final bool titleOnly;

  const _ProfileText({required this.profile, this.titleOnly = false});

  @override
  Widget build(BuildContext context) {
    final title = Text(
      profile.displayName,
      style: const TextStyle(fontWeight: FontWeight.bold),
    );

    if (titleOnly) return title;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        title,
        const SizedBox(height: 4),
        Text(profileDescription(profile)),
      ],
    );
  }
}

class _SwitchProfileButton extends StatelessWidget {
  final bool enabled;
  final VoidCallback onPressed;

  const _SwitchProfileButton({
    required this.enabled,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return FilledButton.icon(
      onPressed: enabled ? onPressed : null,
      icon: const Icon(Icons.swap_horiz),
      label: const Text('Wechseln'),
      style: FilledButton.styleFrom(
        backgroundColor: AppColors.careenaDark,
        foregroundColor: AppColors.white,
        disabledBackgroundColor: AppColors.careenaBorder,
        disabledForegroundColor: AppColors.careenaMuted,
      ),
    );
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