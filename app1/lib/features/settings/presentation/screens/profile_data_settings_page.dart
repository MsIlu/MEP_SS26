import 'package:app1/core/themes/app_colors.dart';
import 'package:flutter/material.dart';

import '../../../authscreen/state/auth_session.dart';
import '../../../profiles/data/profile_api_service.dart';
import '../settings_icons.dart';
import '../widgets/settings_components.dart';
import '../widgets/settings_detail_scaffold.dart';
import 'health_data_settings_page.dart';
import 'personal_data_settings_page.dart';

class ProfileDataSettingsPage extends StatelessWidget {
  final AuthSession? authSession;
  final ProfileApiService? profileApiService;

  const ProfileDataSettingsPage({
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
        authSession?.activeProfile?.displayName ?? 'das aktive Profil';
    final activeProfileId = authSession?.activeProfileId;

    return SettingsDetailScaffold(
      title: 'Profildaten',
      subtitle: 'Angaben für $profileName verwalten.',
      icon: SettingsIcons.personalData,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _ProfileDataCard(
            icon: SettingsIcons.personalData,
            title: '1. Persönliche Angaben',
            child: PersonalDataSettingsForm(
              key: ValueKey('personal-data-$activeProfileId'),
              authSession: authSession,
              profileApiService: profileApiService,
            ),
          ),
          const SizedBox(height: 16),
          _ProfileDataCard(
            icon: SettingsIcons.healthData,
            title: '2. Gesundheitsangaben',
            child: HealthDataSettingsForm(
              key: ValueKey('health-data-$activeProfileId'),
              authSession: authSession,
              profileApiService: profileApiService,
            ),
          ),
        ],
      ),
    );
  }
}

class _ProfileDataCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final Widget child;

  const _ProfileDataCard({
    required this.icon,
    required this.title,
    required this.child,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Material(
      clipBehavior: Clip.antiAlias,
      color: isDark
          ? AppColors.darkElevatedSurface
          : AppColors.careenaNoteBackground,
      borderRadius: BorderRadius.circular(8),
      child: Padding(
        padding: const EdgeInsets.fromLTRB(16, 16, 16, 18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                SettingsIconBadge(icon: icon),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    title,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            child,
          ],
        ),
      ),
    );
  }
}
