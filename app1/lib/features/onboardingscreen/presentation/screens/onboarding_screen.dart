import 'package:app1/features/symptom_diary/data/symptom_repository.dart';
import 'package:flutter/material.dart';
import '../../../../core/themes/theme_controller.dart';
import '../../../../core/widgets/responsive_frame.dart';
import '../../../authscreen/presentation/screens/login_screen.dart';
import '../../../authscreen/presentation/screens/registration_screen.dart';
import '../../../authscreen/presentation/widgets/common/auth_buttons.dart';
import '../../../chatscreen/controllers/chat_controller.dart';
import '../../../chatscreen/presentation/screens/chat_screen.dart';
import '../../../homescreen/presentation/screens/home_screen.dart';
import '../widgets/onboarding_hero_card.dart';
import 'package:app1/core/themes/app_colors.dart';
import '../../../../core/widgets/careena_page_header.dart';
import '../../../authscreen/state/auth_session.dart';
import '../../../authscreen/data/auth_api_service.dart';

/// Entry screen that introduces Careena and routes users into chat or home.
class OnboardingScreen extends StatelessWidget {
  /// Shared chat controller passed forward so later screens keep one session.
  final ChatController chatController;

  /// Shared theme controller used to switch between light and dark mode.
  final ThemeController themeController;

  final AuthSession authSession;

  final AuthApiService authApiService;

  final SymptomRepository symptomRepository;

  const OnboardingScreen({
    super.key,
    required this.chatController,
    required this.themeController,
    required this.authSession,
    required this.authApiService,
    required this.symptomRepository,
  });

  @override
  Widget build(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      backgroundColor: isDarkMode
          ? Theme.of(context).scaffoldBackgroundColor
          : AppColors.onboardingBackgroundLight,
      appBar: CareenaPageHeader(
        title: 'MedBitAid',
        showBack: false,
        trailing: CareenaThemeHeaderAction(
          onPressed: themeController.toggleTheme,
          isDarkMode: themeController.isDarkMode,
        ),
      ),
      body: SafeArea(
        child: ResponsivePageBody(
          maxWidth: 490,
          scrollable: MediaQuery.sizeOf(context).width >= 500,
          padding: const EdgeInsets.symmetric(vertical: 8),
          child: Builder(
            builder: (context) {
              // The auth controls need tighter padding on narrow devices to
              // keep button labels and the divider from feeling cramped.
              final horizontalPadding = ResponsiveBreakpoints.isCompact(context)
                  ? 12.0
                  : 22.0;

              return LayoutBuilder(
                builder: (context, constraints) {
                  final screenSize = MediaQuery.sizeOf(context);
                  final isWideScreen = screenSize.width >= 500;
                  final isShortWideScreen =
                      isWideScreen && constraints.maxHeight < 760;
                  final isShortScreen =
                      !isWideScreen &&
                      (constraints.maxHeight < 780 || screenSize.width < 430);
                  final spacing = isShortScreen ? 8.0 : 14.0;
                  final topOffset = isWideScreen
                      ? isShortWideScreen
                            ? 4.0
                            : 12.0
                      : isShortScreen
                      ? 6.0
                      : 10.0;
                  final authActions = _AuthActions(
                    horizontalPadding: horizontalPadding,
                    isDense: isShortScreen,
                    isWide: isWideScreen,
                    isCompactWide: isShortWideScreen,
                    isDarkMode: isDarkMode,
                    onLogin: () => _navigateToLogin(context),
                    onRegister: () => _navigateToRegistration(context),
                    onOpenHome: () => _navigateToHome(context),
                  );

                  final content = Column(
                    mainAxisSize: isWideScreen
                        ? MainAxisSize.min
                        : MainAxisSize.max,
                    children: [
                      SizedBox(height: topOffset),
                      Align(
                        alignment: Alignment.topCenter,
                        child: OnboardingHeroCard(
                          dense: isShortScreen,
                          compact: isShortWideScreen,
                          onPressed: () => _navigateToChat(context),
                        ),
                      ),
                      SizedBox(
                        height: isShortWideScreen
                            ? 8
                            : isShortScreen
                            ? 20
                            : spacing,
                      ),
                      _OnboardingNotice(
                        horizontalPadding: horizontalPadding,
                        isDense: isShortScreen,
                        isWide: isWideScreen,
                        isCompactWide: isShortWideScreen,
                      ),
                      SizedBox(height: isShortWideScreen || isShortScreen ? 0 : 6),
                      Padding(
                        padding: EdgeInsets.symmetric(
                          horizontal: horizontalPadding,
                        ),
                        child: Align(
                          alignment: Alignment.centerLeft,
                          child: TextButton.icon(
                            onPressed: () => _showPrivacyInfo(context),
                            style: TextButton.styleFrom(
                              minimumSize: Size(0, isShortScreen ? 36 : 42),
                              padding: EdgeInsets.symmetric(
                                horizontal: isWideScreen || isShortScreen
                                    ? 8
                                    : 12,
                                vertical: isWideScreen ? 0 : 4,
                              ),
                              tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                              foregroundColor: isDarkMode
                                  ? AppColors.toolbarButtonBackgroundDark
                                  : AppColors.careenaTeal,
                            ),
                            icon: Icon(
                              Icons.privacy_tip_outlined,
                              size: isWideScreen
                                  ? 14
                                  : isShortScreen
                                  ? 16
                                  : 18,
                            ),
                            label: Text(
                              'Datenschutzhinweise anzeigen',
                              style: TextStyle(
                                fontSize: isWideScreen
                                    ? 12
                                    : isShortScreen
                                    ? 13
                                    : 14,
                              ),
                            ),
                          ),
                        ),
                      ),
                      if (isWideScreen) ...[
                        SizedBox(height: isShortWideScreen ? 4 : 8),
                        ConstrainedBox(
                          constraints: const BoxConstraints(maxWidth: 420),
                          child: authActions,
                        ),
                      ] else
                        Expanded(
                          child: Center(
                            child: authActions,
                          ),
                        ),
                      SizedBox(height: isShortScreen ? 12 : 10),
                    ],
                  );

                  if (isWideScreen) {
                    return SingleChildScrollView(
                      padding: const EdgeInsets.only(bottom: 16),
                      child: Align(
                        alignment: Alignment.topCenter,
                        child: content,
                      ),
                    );
                  }

                  return content;
                },
              );
            },
          ),
        ),
      ),
    );
  }

  /// Opens the chat directly from the onboarding hero call to action.
  void _navigateToChat(BuildContext context) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => ChatScreen(
          controller: chatController,
          themeController: themeController,
          leaveDialogMessage:
              'Wenn du fortfährst, gelangst du zurück zur Startseite. '
              'Der aktuelle Chat wird nicht gespeichert.',
          leaveDialogConfirmLabel: 'Zur Startseite',
        ),
      ),
    );
  }

  /// Opens the login form for returning users.
  void _navigateToLogin(BuildContext context) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => LoginScreen(
          chatController: chatController,
          themeController: themeController,
          authSession: authSession,
          authApiService: authApiService,
          symptomRepository: symptomRepository,
        ),
      ),
    );
  }

  /// Opens the registration form for new users.
  void _navigateToRegistration(BuildContext context) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => RegistrationScreen(
          chatController: chatController,
          themeController: themeController,
          authSession: authSession,
          authApiService: authApiService,
          symptomRepository: symptomRepository,
        ),
      ),
    );
  }

  void _navigateToHome(BuildContext context) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => HomeScreen(
          controller: chatController,
          themeController: themeController,
          authSession: authSession,
        ),
      ),
    );
  }

  void _showPrivacyInfo(BuildContext context) {
    showDialog<void>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('Datenschutzhinweise'),
          content: const SingleChildScrollView(
            child: Text(
              'Careena ist ein KI-Assistent zur ersten Einordnung von Beschwerden '
              'und zur Unterstützung bei möglichen nächsten Schritten.\n\n'
              'Verarbeitungszwecke:\n'
              '- Ersteinschätzung eingegebener Beschwerden\n'
              '- Patientensteuerung und Empfehlung nächster Schritte\n'
              '- personalisierte Unterstützung anhand eingegebener Angaben\n'
              '- Dokumentation von Beschwerden im Symptomtagebuch\n'
              '- Registrierung, Anmeldung und Kontoverwaltung\n\n'
              'Verarbeitete Datenkategorien:\n'
              '- Kontoangaben, insbesondere E-Mail-Adresse und Authentifizierungsdaten\n'
              '- Profildaten, insbesondere Name und Geburtsdatum\n'
              '- medizinisch relevante Angaben, insbesondere biologisches Geschlecht, Größe, Gewicht, Vorerkrankungen und Hinweise\n'
              '- Chatdaten, insbesondere Symptombeschreibungen und Empfehlungen\n'
              '- Symptomtagebuch-Einträge, insbesondere Symptom, Datum, Intensität und Notizen\n'
              '- technische Daten, insbesondere Session-ID und Zugriffstoken\n\n'
              'Das biologische Geschlecht wird ausschließlich als medizinisch '
              'relevanter Kontext für die Ersteinschätzung verwendet.\n\n'
              'Careena ersetzt keine ärztliche Diagnose, Behandlung oder '
              'Notfallversorgung. In akuten Notfällen ist der Notruf 112 '
              'oder medizinisches Fachpersonal zu kontaktieren.\n\n'
              'Diese Hinweise beschreiben den aktuellen Stand und '
              'ersetzen keine vollständige rechtliche Datenschutzerklärung. '
              'Die aktive Zustimmung erfolgt im Registrierungsprozess.',
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Verstanden'),
            ),
          ],
        );
      },
    );
  }
}

class _AuthActions extends StatelessWidget {
  final double horizontalPadding;
  final bool isDense;
  final bool isWide;
  final bool isCompactWide;
  final bool isDarkMode;
  final VoidCallback onLogin;
  final VoidCallback onRegister;
  final VoidCallback onOpenHome;

  const _AuthActions({
    required this.horizontalPadding,
    required this.isDense,
    required this.isWide,
    this.isCompactWide = false,
    required this.isDarkMode,
    required this.onLogin,
    required this.onRegister,
    required this.onOpenHome,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final buttonHeight = isDense ? 50.0 : 56.0;
    final fontSize = isDense ? 16.0 : 18.0;
    final gap = isDense ? 6.0 : 16.0;
    final testLinkFontSize = isWide ? 11.0 : (isDense ? 10.5 : 14.0);
    final testLinkIconSize = isWide ? 14.0 : (isDense ? 13.0 : 18.0);
    final testLinkHeight = isWide ? 22.0 : (isDense ? 24.0 : 40.0);
    final testLink = TextButton.icon(
      onPressed: onOpenHome,
      style: TextButton.styleFrom(
        minimumSize: Size(0, testLinkHeight),
        padding: EdgeInsets.symmetric(
          horizontal: isWide || isDense ? 6 : 8,
          vertical: isWide || isDense ? 0 : 4,
        ),
        tapTargetSize: MaterialTapTargetSize.shrinkWrap,
        foregroundColor: isDarkMode
            ? AppColors.toolbarButtonBackgroundDark
            : AppColors.careenaTeal,
      ),
      icon: Icon(Icons.home_outlined, size: testLinkIconSize),
      label: Text(
        'Test: direkt zur Startseite',
        style: TextStyle(fontSize: testLinkFontSize),
      ),
    );

    if (isWide) {
      return Padding(
        padding: EdgeInsets.symmetric(horizontal: horizontalPadding),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            CareenaButton(
              text: 'Anmelden',
              onPressed: onLogin,
              backgroundColor: colorScheme.surface,
              foregroundColor: colorScheme.onSurface,
              borderRadius: 16,
              elevation: 2,
              height: isCompactWide ? 38 : 44,
              fontSize: isCompactWide ? 14 : 15,
            ),
            SizedBox(height: isCompactWide ? 4 : 8),
            const _CompactAuthDivider(),
            SizedBox(height: isCompactWide ? 4 : 8),
            CareenaButton(
              text: 'Registrieren',
              onPressed: onRegister,
              backgroundColor: colorScheme.surface,
              foregroundColor: colorScheme.onSurface,
              borderRadius: 16,
              elevation: 2,
              height: isCompactWide ? 38 : 44,
              fontSize: isCompactWide ? 14 : 15,
            ),
            const SizedBox(height: 2),
            testLink,
          ],
        ),
      );
    }

    return Padding(
      padding: EdgeInsets.symmetric(horizontal: horizontalPadding),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          CareenaButton(
            text: 'Anmelden',
            onPressed: onLogin,
            backgroundColor: colorScheme.surface,
            foregroundColor: colorScheme.onSurface,
            borderRadius: 16,
            elevation: 2,
            height: buttonHeight,
            fontSize: fontSize,
          ),
          SizedBox(height: gap),
          const AuthDivider(),
          SizedBox(height: gap),
          CareenaButton(
            text: 'Registrieren',
            onPressed: onRegister,
            backgroundColor: colorScheme.surface,
            foregroundColor: colorScheme.onSurface,
            borderRadius: 16,
            elevation: 2,
            height: buttonHeight,
            fontSize: fontSize,
          ),
          SizedBox(height: isDense ? 4 : 10),
          testLink,
        ],
      ),
    );
  }
}

class _CompactAuthDivider extends StatelessWidget {
  const _CompactAuthDivider();

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        SizedBox(
              width: 96,
          child: Divider(color: colorScheme.outlineVariant, thickness: 0.6),
        ),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 18),
          child: Text(
            'oder',
            style: TextStyle(
              fontSize: 12,
              color: colorScheme.onSurfaceVariant,
            ),
          ),
        ),
        SizedBox(
          width: 96,
          child: Divider(color: colorScheme.outlineVariant, thickness: 0.6),
        ),
      ],
    );
  }
}

class _OnboardingNotice extends StatelessWidget {
  final double horizontalPadding;
  final bool isDense;
  final bool isWide;
  final bool isCompactWide;

  const _OnboardingNotice({
    required this.horizontalPadding,
    required this.isDense,
    this.isWide = false,
    this.isCompactWide = false,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Padding(
      padding: EdgeInsets.symmetric(horizontal: horizontalPadding),
      child: Container(
        padding: EdgeInsets.all(
          isCompactWide ? 6 : (isWide ? 8 : (isDense ? 10 : 12)),
        ),
        decoration: BoxDecoration(
          color: isDarkMode ? colorScheme.surface : AppColors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: AppColors.careenaTeal,
            width: 2,
          ),
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(
              Icons.info_outline,
              size: isCompactWide ? 14 : (isWide ? 16 : (isDense ? 18 : 20)),
              color: isDarkMode ? AppColors.white : AppColors.careenaTeal,
            ),
            const SizedBox(width: 8),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Hinweis',
                    style: TextStyle(
                      fontSize: isCompactWide ? 13 : (isDense ? 14 : 15),
                      fontWeight: FontWeight.w900,
                      color: isDarkMode
                          ? AppColors.white
                          : AppColors.careenaTeal,
                    ),
                  ),
                  SizedBox(height: isCompactWide || isDense ? 2 : 4),
                  Text(
                    'Careena unterstützt dich bei der Einordnung deiner Beschwerden. '
                    'Die Anwendung ersetzt keine ärztliche Untersuchung, Diagnose oder Behandlung.',
                    style: TextStyle(
                      fontSize: isCompactWide
                          ? 10.5
                          : (isWide ? 11 : (isDense ? 12 : 13)),
                      height: isWide || isDense ? 1.18 : 1.3,
                      color: colorScheme.onSurface,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
