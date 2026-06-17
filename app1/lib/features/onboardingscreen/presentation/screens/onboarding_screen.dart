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
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      backgroundColor: isDarkMode
          ? Theme.of(context).scaffoldBackgroundColor
          : AppColors.onboardingBackgroundLight,
      appBar: CareenaPageHeader(
        title: 'MedBitAid',
        showBack: false,
        leading: TextButton.icon(
          onPressed: () => _navigateToHome(context),
          style: TextButton.styleFrom(
            foregroundColor: isDarkMode
                ? AppColors.toolbarButtonBackgroundDark
                : AppColors.careenaTeal,
            padding: const EdgeInsets.symmetric(horizontal: 8),
          ),
          icon: const Icon(Icons.home_outlined, size: 18),
          label: const Text(
            'Test',
            style: TextStyle(fontWeight: FontWeight.w800),
          ),
        ),
        trailing: CareenaThemeHeaderAction(
          onPressed: themeController.toggleTheme,
          isDarkMode: themeController.isDarkMode,
        ),
      ),
      body: SafeArea(
        child: ResponsivePageBody(
          maxWidth: 560,
          scrollable: false,
          padding: const EdgeInsets.symmetric(vertical: 12),
          child: Builder(
            builder: (context) {
              // The auth controls need tighter padding on narrow devices to
              // keep button labels and the divider from feeling cramped.
              final horizontalPadding = ResponsiveBreakpoints.isCompact(context)
                  ? 12.0
                  : 22.0;

              return Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  OnboardingHeroCard(onPressed: () => _navigateToChat(context)),
                  const SizedBox(height: 18),
                  Padding(
                    padding: EdgeInsets.symmetric(
                      horizontal: horizontalPadding,
                    ),
                    child: Column(
                      children: [
                        CareenaButton(
                          text: 'Anmelden',
                          onPressed: () => _navigateToLogin(context),
                          backgroundColor: colorScheme.surface,
                          foregroundColor: colorScheme.onSurface,
                          borderRadius: 22,
                          elevation: 2,
                        ),
                        const SizedBox(height: 16),
                        const AuthDivider(),
                        const SizedBox(height: 16),
                        CareenaButton(
                          text: 'Registrieren',
                          onPressed: () => _navigateToRegistration(context),
                          backgroundColor: colorScheme.surface,
                          foregroundColor: colorScheme.onSurface,
                          borderRadius: 22,
                          elevation: 2,
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 10),
                ],
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
}
