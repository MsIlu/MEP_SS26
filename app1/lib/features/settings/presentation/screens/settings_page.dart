import 'package:flutter/material.dart';

import '../../../../core/themes/theme_controller.dart';
import '../../../../core/widgets/careena_page_header.dart';
import '../../../../core/widgets/responsive_frame.dart';
import '../../../authscreen/data/auth_api_service.dart';
import '../../../authscreen/state/auth_session.dart';
import '../../../profiles/data/profile_api_service.dart';
import '../settings_icons.dart';
import '../widgets/display_settings_section.dart';
import '../widgets/profile_settings_section.dart';
import '../widgets/settings_components.dart';
import '../widgets/settings_detail_scaffold.dart';
import 'settings_text_page.dart';

class SettingsPage extends StatefulWidget {
  final ThemeController themeController;
  final AuthSession? authSession;
  final AuthApiService? authApiService;
  final ProfileApiService? profileApiService;

  const SettingsPage({
    super.key,
    required this.themeController,
    this.authSession,
    this.authApiService,
    this.profileApiService,
  });

  @override
  State<SettingsPage> createState() => _SettingsPageState();
}

class _SettingsPageState extends State<SettingsPage> {
  final _searchController = TextEditingController();
  String _query = '';

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: Listenable.merge([
        widget.themeController,
        if (widget.authSession != null) widget.authSession!,
      ]),
      builder: (context, _) {
        final simpleView = widget.themeController.isSimpleView;
        final visibleItems = _items(
          context,
        ).where((item) => item.matches(_query)).toList();

        return Scaffold(
          appBar: CareenaPageHeader(
            title: 'Einstellungen',
            trailing: CareenaThemeHeaderAction(
              onPressed: widget.themeController.toggleTheme,
              isDarkMode: widget.themeController.isDarkMode,
            ),
          ),
          body: ResponsivePageBody(
            maxWidth: 620,
            scrollable: true,
            padding: EdgeInsets.fromLTRB(
              simpleView ? 20 : 18,
              22,
              simpleView ? 20 : 18,
              28,
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                SettingsSearchField(
                  controller: _searchController,
                  simpleView: simpleView,
                  onChanged: (value) {
                    setState(() => _query = value.trim().toLowerCase());
                  },
                ),
                const SizedBox(height: 20),
                if (visibleItems.isEmpty)
                  const SettingsEmptySearchResult()
                else
                  SettingsPanel(
                    children: [
                      for (final item in visibleItems)
                        SettingsMenuTile(
                          icon: item.icon,
                          title: item.title,
                          description: item.description,
                          trailing: item.trailing,
                          onTap: item.onTap,
                          isSimpleView: simpleView,
                        ),
                    ],
                  ),
              ],
            ),
          ),
          bottomNavigationBar: SettingsLogoutAction(
            simpleView: simpleView,
            onPressed: () => _logout(context),
          ),
        );
      },
    );
  }

  List<_SettingsItem> _items(BuildContext context) {
    final session = widget.authSession;
    final activeProfile = session?.activeProfile?.displayName;

    return [
      _SettingsItem(
        icon: SettingsIcons.profiles,
        title: 'Profile und persönliche Daten',
        description: activeProfile == null
            ? 'Eigenes oder betreutes Profil verwalten'
            : 'Aktives Profil: $activeProfile',
        keywords: const ['konto', 'account', 'profil', 'persönlich'],
        onTap: () => _open(
          context,
          SettingsDetailScaffold(
            title: 'Profile',
            subtitle: 'Verwalte Profile und persönliche Angaben.',
            icon: SettingsIcons.profiles,
            showSectionHeader: false,
            child: ProfileSettingsSection(
              authSession: session,
              profileApiService: widget.profileApiService,
            ),
          ),
        ),
      ),
      _SettingsItem(
        icon: SettingsIcons.simpleView,
        title: 'Einfache Ansicht',
        description: widget.themeController.isSimpleView
            ? 'Große Elemente und reduzierte Navigation'
            : 'Für bessere Lesbarkeit und Bedienung',
        keywords: const ['barrierefreiheit', 'einfach', 'groß', 'sehen'],
        trailing: Switch.adaptive(
          value: widget.themeController.isSimpleView,
          onChanged: widget.themeController.setSimpleView,
        ),
        onTap: () => widget.themeController.setSimpleView(
          !widget.themeController.isSimpleView,
        ),
      ),
      _SettingsItem(
        icon: SettingsIcons.display,
        title: 'Darstellung',
        description: 'Hell, dunkel oder automatisch',
        keywords: const ['aussehen', 'darstellung', 'dark', 'light', 'theme'],
        onTap: () => _open(
          context,
          SettingsDetailScaffold(
            title: 'Darstellung',
            subtitle: 'Wähle die Ansicht, die du gut erkennen kannst.',
            icon: SettingsIcons.display,
            showSectionHeader: false,
            child: DisplaySettingsSection(
              themeController: widget.themeController,
              showSimpleView: false,
            ),
          ),
        ),
      ),
      _SettingsItem(
        icon: SettingsIcons.privacy,
        title: 'Datenschutz und Sicherheit',
        description: 'Umgang mit deinen Daten',
        keywords: const ['datenschutz', 'privacy', 'sicherheit'],
        onTap: () => _open(context, const SettingsTextPage.privacy()),
      ),
      _SettingsItem(
        icon: SettingsIcons.help,
        title: 'Hilfe und Support',
        description: 'Antworten und Kontaktmöglichkeiten',
        keywords: const ['hilfe', 'support', 'kontakt'],
        onTap: () => _open(context, const SettingsTextPage.help()),
      ),
      _SettingsItem(
        icon: SettingsIcons.about,
        title: 'Über Careena',
        description: 'Impressum, Barrierefreiheit und App-Version',
        keywords: const ['über', 'about', 'impressum', 'barrierefreiheit'],
        onTap: () => _open(context, const _AboutSettingsPage()),
      ),
    ];
  }

  void _open(BuildContext context, Widget page) {
    Navigator.push(context, MaterialPageRoute(builder: (context) => page));
  }

  void _logout(BuildContext context) {
    widget.authApiService?.logout();
    widget.authSession?.clear();
    Navigator.maybePop(context);
  }
}

class _AboutSettingsPage extends StatelessWidget {
  const _AboutSettingsPage();

  @override
  Widget build(BuildContext context) {
    return SettingsDetailScaffold(
      title: 'Über Careena',
      subtitle: 'Informationen und rechtliche Hinweise.',
      icon: SettingsIcons.about,
      child: SettingsPanel(
        children: [
          SettingsLinkTile(
            icon: Icons.accessible_forward,
            title: 'Barrierefreiheit',
            description: 'Bedienung und Rückmeldung',
            page: const SettingsTextPage.accessibility(),
          ),
          SettingsLinkTile(
            icon: Icons.info_outline,
            title: 'Impressum',
            description: 'Angaben zum Anbieter',
            page: const SettingsTextPage.imprint(),
          ),
          SettingsLinkTile(
            icon: Icons.phone_android,
            title: 'App-Informationen',
            description: 'Careena und App-Version',
            page: const SettingsTextPage.about(),
          ),
        ],
      ),
    );
  }
}

class _SettingsItem {
  final IconData icon;
  final String title;
  final String description;
  final List<String> keywords;
  final Widget? trailing;
  final VoidCallback onTap;

  const _SettingsItem({
    required this.icon,
    required this.title,
    required this.description,
    required this.keywords,
    required this.onTap,
    this.trailing,
  });

  bool matches(String query) {
    if (query.isEmpty) return true;
    return '$title $description ${keywords.join(' ')}'.toLowerCase().contains(
      query,
    );
  }
}
