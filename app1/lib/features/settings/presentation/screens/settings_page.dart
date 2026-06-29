import 'package:app1/app/app_dependencies_scope.dart';
import 'package:app1/core/themes/app_colors.dart';
import 'package:app1/features/calendar_overview/presentation/screens/calendar_overview_page.dart';
import 'package:app1/features/chatscreen/presentation/screens/chat_history_screen.dart';
import 'package:app1/features/homescreen/presentation/screens/home_screen.dart';
import 'package:app1/features/homescreen/presentation/widgets/custom_bottom_nav.dart';
import 'package:flutter/material.dart';

import '../../../../core/themes/theme_controller.dart';
import '../../../../core/widgets/careena_page_header.dart';
import '../../../../core/widgets/careena_snack_bar.dart';
import '../../../../core/widgets/responsive_frame.dart';
import '../../../authscreen/data/auth_api_service.dart';
import '../../../authscreen/state/auth_session.dart';
import '../../../profiles/data/profile_api_service.dart';
import '../settings_icons.dart';
import '../widgets/display_settings_section.dart';
import '../widgets/profile_settings_section.dart';
import '../widgets/settings_components.dart';
import '../widgets/settings_detail_scaffold.dart';
import 'medical_glossary_page.dart';
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
    final dependencies = AppDependenciesScope.maybeOf(context);
    final authSession = widget.authSession ?? dependencies?.authSession;
    final authApiService =
        widget.authApiService ?? dependencies?.authApiService;

    return AnimatedBuilder(
      animation: Listenable.merge([
        widget.themeController,
        ?authSession,
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
              96,
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
                const SizedBox(height: 20),
                SettingsLogoutAction(
                  simpleView: simpleView,
                  onPressed: () => _logout(context),
                ),
                if (authSession?.isAuthenticated == true &&
                    authApiService != null)
                  Center(
                    child: TextButton.icon(
                      key: const ValueKey('settings-delete-account-button'),
                      onPressed: () =>
                          _deleteAccount(context, authSession!, authApiService),
                      icon: const Icon(Icons.delete_forever),
                      label: const Text('Account löschen'),
                      style: TextButton.styleFrom(
                        foregroundColor: AppColors.warningRed,
                      ),
                    ),
                  ),
              ],
            ),
          ),
          bottomNavigationBar: CustomBottomNav(
            // Settings is the fourth primary destination in the shared app nav.
            currentIndex: 3,
            isSimpleView: simpleView,
            onTap: _onBottomNavigationTap,
          ),
        );
      },
    );
  }

  void _onBottomNavigationTap(int index) {
    if (index == 3) return;
    if (index == 0) {
      _openHome();
      return;
    }

    final dependencies = AppDependenciesScope.maybeOf(context);

    if (index == 1) {
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(
          builder: (context) => CalendarOverviewPage(
            themeController: widget.themeController,
            apiClient: dependencies?.apiClient,
            authSession: dependencies?.authSession,
          ),
        ),
      );
      return;
    }

    if (index == 2) {
      final activeProfileId = dependencies?.authSession.activeProfileId;
      if (dependencies == null || activeProfileId == null) {
        _showNavigationUnavailable();
        return;
      }

      Navigator.of(context).pushReplacement(
        MaterialPageRoute(
          builder: (context) => ChatHistoryScreen(
            themeController: widget.themeController,
            profileId: activeProfileId,
            repository: dependencies.chatController.chatHistoryRepository,
          ),
        ),
      );
    }
  }

  void _showNavigationUnavailable() {
    showCareenaSnackBar(context, 'Dieser Bereich ist aktuell nicht verfügbar.');
  }

  void _openHome() {
    final dependencies = AppDependenciesScope.maybeOf(context);
    if (dependencies == null) {
      // Isolated widget tests can still fall back to the existing route stack.
      Navigator.of(context).popUntil((route) => route.isFirst);
      return;
    }

    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(
        builder: (context) => HomeScreen(
          controller: dependencies.chatController,
          themeController: widget.themeController,
          apiClient: dependencies.apiClient,
          authSession: dependencies.authSession,
          authApiService: dependencies.authApiService,
          symptomApiService: dependencies.symptomApiService,
        ),
      ),
      (route) => false,
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
        icon: SettingsIcons.language,
        title: 'Sprache ändern',
        description: 'Deutsch ist aktuell ausgewählt',
        keywords: const ['sprache', 'language', 'deutsch', 'englisch'],
        onTap: () => _open(context, const _LanguageSettingsPage()),
      ),
      _SettingsItem(
        icon: SettingsIcons.glossary,
        title: 'Medizinisches Glossar',
        description: 'Begriffe alphabetisch erklärt',
        keywords: const ['glossar', 'medizin', 'begriff', 'lexikon'],
        onTap: () => _open(context, const MedicalGlossaryPage()),
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
    Navigator.of(
      context,
      rootNavigator: true,
    ).popUntil((route) => route.isFirst);
  }

  Future<void> _deleteAccount(
    BuildContext context,
    AuthSession authSession,
    AuthApiService authApiService,
  ) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (dialogContext) {
        final isDark = Theme.of(dialogContext).brightness == Brightness.dark;
        return AlertDialog(
          backgroundColor: isDark
              ? AppColors.warningEmergencyBackgroundDark
              : AppColors.warningBackground,
          title: const Row(
            children: [
              Icon(
                Icons.warning_amber_rounded,
                color: AppColors.warningRed,
                size: 30,
              ),
              SizedBox(width: 12),
              Expanded(child: Text('Account löschen?')),
            ],
          ),
          content: const Text(
            'Dein Account und alle ausschließlich von dir verwalteten Profile '
            'werden deaktiviert. Du kannst dich danach nicht mehr anmelden.',
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
              child: const Text('Account löschen'),
            ),
          ],
        );
      },
    );

    if (confirmed != true || !context.mounted) return;

    try {
      await authApiService.deleteAccount();
      authSession.clear();
      if (!context.mounted) return;
      Navigator.of(
        context,
        rootNavigator: true,
      ).popUntil((route) => route.isFirst);
    } catch (_) {
      if (!context.mounted) return;
      showCareenaSnackBar(
        context,
        'Der Account konnte nicht gelöscht werden. Bitte versuche es erneut.',
      );
    }
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

class _LanguageSettingsPage extends StatelessWidget {
  const _LanguageSettingsPage();

  @override
  Widget build(BuildContext context) {
    return const SettingsDetailScaffold(
      title: 'Sprache ändern',
      subtitle: 'Wähle die Sprache für Careena.',
      icon: SettingsIcons.language,
      child: SettingsPanel(
        children: [
          _LanguageOptionTile(
            title: 'Deutsch',
            description: 'Aktuelle App-Sprache',
            isSelected: true,
          ),
          _LanguageOptionTile(
            title: 'English',
            description: 'Demnächst verfügbar',
          ),
          _LanguageOptionTile(
            title: 'Türkçe',
            description: 'Demnächst verfügbar',
          ),
        ],
      ),
    );
  }
}

class _LanguageOptionTile extends StatelessWidget {
  final String title;
  final String description;
  final bool isSelected;

  const _LanguageOptionTile({
    required this.title,
    required this.description,
    this.isSelected = false,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return ListTile(
      leading: SettingsIconBadge(
        icon: isSelected ? Icons.check_circle_outline : Icons.translate,
        isActive: isSelected,
      ),
      title: Text(
        title,
        style: TextStyle(
          fontWeight: FontWeight.w800,
          color: colorScheme.onSurface,
        ),
      ),
      subtitle: Text(
        description,
        style: TextStyle(color: colorScheme.onSurfaceVariant),
      ),
      trailing: isSelected
          ? const Icon(Icons.check, color: AppColors.careenaTeal)
          : const Icon(Icons.lock_outline, color: AppColors.careenaMuted),
      enabled: isSelected,
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
