import 'package:flutter/material.dart';

import '../../../../core/themes/theme_controller.dart';
import '../../../../core/widgets/careena_page_header.dart';
import '../../../../core/widgets/responsive_frame.dart';
import '../../../authscreen/data/auth_api_service.dart';
import '../../../authscreen/state/auth_session.dart';
import '../widgets/display_settings_section.dart';
import '../widgets/profile_settings_section.dart';
import '../widgets/settings_info_section.dart';

class SettingsPage extends StatelessWidget {
  final ThemeController themeController;
  final AuthSession? authSession;
  final AuthApiService? authApiService;

  const SettingsPage({
    super.key,
    required this.themeController,
    this.authSession,
    this.authApiService,
  });

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: themeController,
      builder: (context, _) {
        return Scaffold(
          appBar: CareenaPageHeader(
            title: 'Einstellungen',
            trailing: CareenaThemeHeaderAction(
              onPressed: themeController.toggleTheme,
              isDarkMode: themeController.isDarkMode,
            ),
          ),
          body: ResponsivePageBody(
            maxWidth: 720,
            scrollable: true,
            padding: EdgeInsets.fromLTRB(
              themeController.isSimpleView ? 20 : 16,
              20,
              themeController.isSimpleView ? 20 : 16,
              32,
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                DisplaySettingsSection(themeController: themeController),
                const SizedBox(height: 28),
                ProfileSettingsSection(authSession: authSession),
                const SizedBox(height: 28),
                const SettingsInfoSection(),
                const SizedBox(height: 28),
                FilledButton.icon(
                  onPressed: () => _logout(context),
                  icon: const Icon(Icons.logout),
                  label: const Text('Abmelden'),
                  style: FilledButton.styleFrom(
                    minimumSize: Size.fromHeight(
                      themeController.isSimpleView ? 64 : 52,
                    ),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  void _logout(BuildContext context) {
    authApiService?.logout();
    authSession?.clear();
    Navigator.maybePop(context);
  }
}