import 'package:flutter/material.dart';

import '../../../authscreen/state/auth_session.dart';
import '../../../profiles/data/profile_api_service.dart';
import '../screens/profile_data_settings_page.dart';
import '../settings_icons.dart';
import 'active_profile_overview.dart';
import 'create_managed_profile_button.dart';
import 'profile_preview.dart';
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
          onPressed: () => Navigator.push(
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
      ],
    );
  }
}
