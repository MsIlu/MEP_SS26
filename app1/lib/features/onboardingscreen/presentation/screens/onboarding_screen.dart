import 'package:app1/features/symptom_diary/data/symptom_repository.dart';
import 'package:flutter/material.dart';
import '../../../../core/themes/theme_controller.dart';
import '../../../../core/widgets/responsive_frame.dart';
import '../../../authscreen/presentation/screens/login_screen.dart';
import '../../../authscreen/presentation/screens/registration_screen.dart';
import '../../../authscreen/presentation/widgets/common/auth_buttons.dart';
import '../../../chatscreen/controllers/chat_controller.dart';
import '../../../chatscreen/presentation/screens/chat_screen.dart';
import '../widgets/onboarding_hero_card.dart';
import 'package:app1/core/themes/app_colors.dart';
import '../../../../core/widgets/careena_page_header.dart';
import '../../../authscreen/state/auth_session.dart';
import '../../../authscreen/data/auth_api_service.dart';

/// Entry screen that introduces Careena and routes users into chat or auth flows.
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
    final screenWidth = MediaQuery.sizeOf(context).width;
    final useDesktopLayout = screenWidth >= 640;

    return Scaffold(
      backgroundColor: isDarkMode
          ? Theme.of(context).scaffoldBackgroundColor
          : AppColors.onboardingBackgroundLight,
      appBar: CareenaPageHeader(title: 'MedBitAid', showBack: false),
      body: SafeArea(
        child: ResponsivePageBody(
          maxWidth: screenWidth >= 1100 ? 1040 : (useDesktopLayout ? 900 : 490),
          scrollable: true,
          padding: EdgeInsets.symmetric(
            horizontal: useDesktopLayout ? 24 : 0,
            vertical: useDesktopLayout ? 18 : 8,
          ),
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
                  final safeAreaPadding = MediaQuery.paddingOf(context);
                  final viewportHeight = constraints.maxHeight.isFinite
                      ? constraints.maxHeight
                      : (screenSize.height -
                                kToolbarHeight -
                                safeAreaPadding.vertical -
                                (useDesktopLayout ? 36 : 16))
                            .clamp(0.0, double.infinity);
                  final isWideScreen = screenSize.width >= 500;
                  final isShortWideScreen =
                      isWideScreen &&
                      (viewportHeight < 760 || screenSize.width < 640);
                  final isShortScreen =
                      !isWideScreen &&
                      (viewportHeight < 780 || screenSize.width < 430);
                  final isFullDesktop = screenSize.width >= 1100;
                  final spacing = isShortScreen ? 8.0 : 14.0;
                  final topOffset = isWideScreen
                      ? isShortWideScreen
                            ? 4.0
                            : 12.0
                      : isShortScreen
                      ? 18.0
                      : 22.0;
                  final authActions = _AuthActions(
                    horizontalPadding: horizontalPadding,
                    isDense: isShortScreen,
                    isWide: isWideScreen,
                    isCompactWide:
                        isShortWideScreen ||
                        (useDesktopLayout && !isFullDesktop),
                    onLogin: () => _navigateToLogin(context),
                    onRegister: () => _navigateToRegistration(context),
                  );
                  final privacyButton = Padding(
                    padding: EdgeInsets.symmetric(
                      horizontal: horizontalPadding,
                    ),
                    child: Align(
                      alignment: Alignment.center,
                      child: TextButton.icon(
                        onPressed: () => _showPrivacyInfo(context),
                        style: TextButton.styleFrom(
                          minimumSize: Size(0, isShortScreen ? 30 : 42),
                          padding: EdgeInsets.symmetric(
                            horizontal: isWideScreen || isShortScreen ? 8 : 12,
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
                              ? 14
                              : 18,
                        ),
                        label: Text(
                          'Datenschutzhinweise anzeigen',
                          style: TextStyle(
                            fontSize: isWideScreen
                                ? 12
                                : isShortScreen
                                ? 12
                                : 14,
                          ),
                        ),
                      ),
                    ),
                  );
                  final isTwoColumnLayout = screenSize.width >= 640;
                  final isNarrowTwoColumn =
                      isTwoColumnLayout && screenSize.width < 900;
                  final placeNoticeBelowActions =
                      isShortWideScreen || isShortScreen;

                  if (isTwoColumnLayout) {
                    return ConstrainedBox(
                      constraints: BoxConstraints(minHeight: viewportHeight),
                      child: Center(
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.center,
                          children: [
                            Expanded(
                              flex: 7,
                              child: OnboardingHeroCard(
                                compact: !isFullDesktop,
                                onPressed: () => _navigateToChat(context),
                              ),
                            ),
                            SizedBox(width: isNarrowTwoColumn ? 24 : 48),
                            Expanded(
                              flex: isNarrowTwoColumn ? 6 : 5,
                              child: Column(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  ConstrainedBox(
                                    constraints: const BoxConstraints(
                                      maxWidth: 390,
                                    ),
                                    child: authActions,
                                  ),
                                  SizedBox(height: isShortWideScreen ? 30 : 50),
                                  _OnboardingNotice(
                                    horizontalPadding: horizontalPadding,
                                    isDense: true,
                                    isWide: true,
                                    isCompactWide: !isFullDesktop,
                                  ),
                                  SizedBox(height: isShortWideScreen ? 0 : 4),
                                  privacyButton,
                                ],
                              ),
                            ),
                          ],
                        ),
                      ),
                    );
                  }
                  final onboardingNotice = _OnboardingNotice(
                    horizontalPadding: horizontalPadding,
                    isDense: isShortScreen,
                    isWide: isWideScreen,
                    isCompactWide: isShortWideScreen,
                  );
                  final authActionsSection = <Widget>[
                    if (isWideScreen) ...[
                      SizedBox(height: isShortWideScreen ? 4 : 8),
                      ConstrainedBox(
                        constraints: const BoxConstraints(maxWidth: 420),
                        child: authActions,
                      ),
                    ] else ...[
                      SizedBox(height: isShortScreen ? 8 : 18),
                      authActions,
                    ],
                  ];
                  final content = Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      SizedBox(height: topOffset),
                      Align(
                        alignment: Alignment.topCenter,
                        child: ConstrainedBox(
                          constraints: BoxConstraints(
                            maxWidth: isWideScreen ? double.infinity : 390,
                          ),
                          child: OnboardingHeroCard(
                            dense: isShortScreen,
                            compact: isShortWideScreen,
                            onPressed: () => _navigateToChat(context),
                          ),
                        ),
                      ),
                      SizedBox(
                        height: isShortWideScreen
                            ? 20
                            : isShortScreen
                            ? 18
                            : spacing,
                      ),
                      if (placeNoticeBelowActions) ...[
                        ...authActionsSection,
                        SizedBox(height: isShortScreen ? 4 : 22),
                        onboardingNotice,
                        SizedBox(
                          height: isShortWideScreen || isShortScreen ? 0 : 6,
                        ),
                        privacyButton,
                      ] else ...[
                        onboardingNotice,
                        SizedBox(
                          height: isShortWideScreen || isShortScreen ? 0 : 6,
                        ),
                        privacyButton,
                        ...authActionsSection,
                      ],
                      SizedBox(height: isShortScreen ? 12 : 10),
                    ],
                  );

                  if (isWideScreen) {
                    return ConstrainedBox(
                      constraints: BoxConstraints(minHeight: viewportHeight),
                      child: Align(
                        alignment: Alignment.center,
                        child: Padding(
                          padding: const EdgeInsets.only(bottom: 16),
                          child: content,
                        ),
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
  final VoidCallback onLogin;
  final VoidCallback onRegister;

  const _AuthActions({
    required this.horizontalPadding,
    required this.isDense,
    required this.isWide,
    this.isCompactWide = false,
    required this.onLogin,
    required this.onRegister,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final buttonHeight = isDense ? 50.0 : 56.0;
    final fontSize = isDense ? 16.0 : 18.0;
    final gap = isDense ? 12.0 : 16.0;

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
              height: isCompactWide ? 60 : 42,
              fontSize: isCompactWide ? 15 : 17,
            ),
            SizedBox(height: isCompactWide ? 10 : 34),
            const _CompactAuthDivider(),
            SizedBox(height: isCompactWide ? 10 : 34),
            CareenaButton(
              text: 'Registrieren',
              onPressed: onRegister,
              backgroundColor: colorScheme.surface,
              foregroundColor: colorScheme.onSurface,
              borderRadius: 16,
              elevation: 2,
              height: isCompactWide ? 60 : 42,
              fontSize: isCompactWide ? 15 : 17,
            ),
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
          const _ShortAuthDivider(),
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
        Expanded(
          child: Divider(color: colorScheme.outlineVariant, thickness: 0.6),
        ),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 14),
          child: Text(
            'oder',
            style: TextStyle(fontSize: 12, color: colorScheme.onSurfaceVariant),
          ),
        ),
        Expanded(
          child: Divider(color: colorScheme.outlineVariant, thickness: 0.6),
        ),
      ],
    );
  }
}

class _ShortAuthDivider extends StatelessWidget {
  const _ShortAuthDivider();

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    final dividerColor = isDarkMode
        ? colorScheme.outlineVariant
        : AppColors.greyShade500;
    final textColor = isDarkMode
        ? colorScheme.onSurfaceVariant
        : AppColors.careenaBody;

    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        SizedBox(
          width: 104,
          child: Divider(color: dividerColor, thickness: 0.6),
        ),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 12),
          child: Text('oder', style: TextStyle(fontSize: 14, color: textColor)),
        ),
        SizedBox(
          width: 104,
          child: Divider(color: dividerColor, thickness: 0.6),
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
          isCompactWide ? 10 : (isWide ? 16 : (isDense ? 8 : 10)),
        ),
        decoration: BoxDecoration(
          color: isDarkMode ? colorScheme.surface : AppColors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: AppColors.careenaTeal, width: 2),
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(
              Icons.info_outline,
              size: isCompactWide ? 13 : (isWide ? 18 : (isDense ? 15 : 18)),
              color: isDarkMode ? AppColors.white : AppColors.careenaTeal,
            ),
            SizedBox(width: isDense ? 6 : 8),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Hinweis',
                    style: TextStyle(
                      fontSize: isCompactWide ? 12 : (isDense ? 13 : 15),
                      fontWeight: FontWeight.w900,
                      color: isDarkMode
                          ? AppColors.white
                          : AppColors.careenaTeal,
                    ),
                  ),
                  SizedBox(height: isCompactWide || isDense ? 1 : 6),
                  Text(
                    'Careena unterstützt dich bei der Einordnung deiner Beschwerden. '
                    'Die Anwendung ersetzt keine ärztliche Untersuchung, Diagnose oder Behandlung.',
                    style: TextStyle(
                      fontSize: isCompactWide
                          ? 9.8
                          : (isWide ? 12.5 : (isDense ? 10.8 : 12.2)),
                      height: isWide || isDense ? 1.18 : 1.24,
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
