import 'dart:async';

import 'package:app1/app/app_dependencies_scope.dart';
import 'package:app1/app/app_page_store.dart';
import 'package:app1/features/appointmentscreen/presentation/screens/appointment_screen.dart';
import 'package:app1/features/calendar_overview/presentation/screens/calendar_overview_page.dart';
import 'package:app1/features/chatscreen/presentation/screens/chat_history_screen.dart';
import 'package:app1/features/chatscreen/presentation/screens/chat_screen.dart';
import 'package:app1/features/documents/presentation/screens/documents_screen.dart';
import 'package:app1/features/homescreen/presentation/screens/home_screen.dart';
import 'package:app1/features/medication_plan/presentation/screens/medication_plan_page.dart';
import 'package:app1/features/settings/presentation/screens/settings_page.dart';
import 'package:app1/features/symptom_diary/data/symptom_repository.dart';
import 'package:app1/features/symptom_diary/presentation/screens/symptom_diary_page.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'app/app_dependencies.dart';
import 'core/themes/app_theme.dart';
import 'core/themes/theme_controller.dart';
import 'features/chatscreen/controllers/chat_controller.dart';
import 'features/onboardingscreen/presentation/screens/onboarding_screen.dart';
import 'features/authscreen/state/auth_session.dart';
import 'features/authscreen/data/auth_api_service.dart';
import 'features/authscreen/presentation/screens/login_screen.dart';
import 'features/authscreen/presentation/screens/registration_screen.dart';

void main() {
  runApp(const MyApp());
}

/// Root widget for the Careena app.
class MyApp extends StatelessWidget {
  final ChatController? chatController;
  final AuthApiService? authApiService;

  const MyApp({super.key, this.chatController, this.authApiService});

  @override
  Widget build(BuildContext context) {
    return _AppBoot(
      externalChatController: chatController,
      externalAuthApiService: authApiService,
    );
  }
}

class _AppBoot extends StatefulWidget {
  final ChatController? externalChatController;
  final AuthApiService? externalAuthApiService;

  const _AppBoot({this.externalChatController, this.externalAuthApiService});

  @override
  State<_AppBoot> createState() => _AppBootState();
}

class _AppBootState extends State<_AppBoot> {
  late final AppDependencies? _ownedDependencies;
  late final ChatController _chatController;
  late final ThemeController _themeController;
  late final AuthSession _authSession;
  late final AuthApiService _authApiService;
  late final SymptomRepository _symptomRepository;
  late final Future<_InitialAppState> _initialState;
  int? _loadedThemeProfileId;

  @override
  void initState() {
    super.initState();

    _authSession = AuthSession();
    _themeController = ThemeController();
    _symptomRepository = SymptomRepository();

    _ownedDependencies =
        widget.externalChatController == null &&
            widget.externalAuthApiService == null
        ? AppDependencies(
            authSession: _authSession,
            symptomRepository: _symptomRepository,
          )
        : null;

    _chatController =
        widget.externalChatController ?? _ownedDependencies!.chatController;

    _authApiService =
        widget.externalAuthApiService ?? _ownedDependencies!.authApiService;

    _authSession.addListener(_handleAuthSessionChanged);
    _initialState = _loadInitialState();
  }

  @override
  void dispose() {
    _themeController.dispose();
    _authSession.removeListener(_handleAuthSessionChanged);
    _authSession.dispose();
    _ownedDependencies?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AppDependenciesScope(
      dependencies: _ownedDependencies!,
      child: AnimatedBuilder(
        animation: _themeController,
        builder: (context, _) {
          return FocusTraversalGroup(
            policy: ReadingOrderTraversalPolicy(),
            child: Shortcuts(
              shortcuts: const {
                SingleActivator(LogicalKeyboardKey.arrowDown):
                    DirectionalFocusIntent(TraversalDirection.down),
                SingleActivator(LogicalKeyboardKey.arrowUp):
                    DirectionalFocusIntent(TraversalDirection.up),
                SingleActivator(LogicalKeyboardKey.arrowRight):
                    DirectionalFocusIntent(TraversalDirection.right),
                SingleActivator(LogicalKeyboardKey.arrowLeft):
                    DirectionalFocusIntent(TraversalDirection.left),
              },
              child: MaterialApp(
                debugShowCheckedModeBanner: false,
                title: 'Careena',
                locale: const Locale('de', 'DE'),
                supportedLocales: const [Locale('de', 'DE')],
                localizationsDelegates: GlobalMaterialLocalizations.delegates,
                theme: AppTheme.lightTheme,
                darkTheme: AppTheme.darkTheme,
                themeMode: _themeController.themeMode,
                home: FutureBuilder<_InitialAppState>(
                  future: _initialState,
                  builder: (context, snapshot) {
                    if (!snapshot.hasData) {
                      return const Scaffold(
                        body: Center(child: CircularProgressIndicator()),
                      );
                    }

                    final initialState = snapshot.data!;
                    if (!initialState.isAuthenticated) {
                      return _buildUnauthenticatedPage(
                        initialState.currentPage ?? AppPage.onboarding,
                      );
                    }

                    return _buildAuthenticatedPage(
                      initialState.currentPage ?? AppPage.home,
                    );
                  },
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  Future<_InitialAppState> _loadInitialState() async {
    final restoredSession = await _authSession.restorePersistedSession();
    await _syncProfileDisplaySettings();
    final currentPage = await AppPageStore.loadCurrentPage();

    return _InitialAppState(
      isAuthenticated: restoredSession,
      currentPage: currentPage,
    );
  }

  Future<void> _syncProfileDisplaySettings() async {
    final profileId = _authSession.activeProfileId;
    if (_loadedThemeProfileId == profileId) return;

    await _themeController.loadProfileSettings(profileId);
    _loadedThemeProfileId = profileId;
  }

  void _handleAuthSessionChanged() {
    unawaited(_syncProfileDisplaySettings());
  }

  Widget _buildAuthenticatedPage(AppPage page) {
    switch (page) {
      case AppPage.onboarding:
      case AppPage.login:
      case AppPage.registration:
        return _buildHomeScreen();
      case AppPage.calendar:
        return CalendarOverviewPage(
          themeController: _themeController,
          apiClient: _ownedDependencies?.apiClient,
          authSession: _authSession,
          symptomRepository: _symptomRepository,
        );
      case AppPage.history:
        final profileId = _authSession.activeProfileId;
        if (profileId == null) return _buildHomeScreen();
        return ChatHistoryScreen(
          themeController: _themeController,
          chatController: _chatController,
          repository: _chatController.chatHistoryRepository,
          profileId: profileId,
        );
      case AppPage.chat:
        return ChatScreen(
          controller: _chatController,
          themeController: _themeController,
        );
      case AppPage.settings:
        return SettingsPage(
          themeController: _themeController,
          authSession: _authSession,
          authApiService: _authApiService,
        );
      case AppPage.documents:
        return DocumentsScreen(
          authSession: _authSession,
          themeController: _themeController,
        );
      case AppPage.appointments:
        return AppointmentScreen(
          authSession: _authSession,
          themeController: _themeController,
        );
      case AppPage.symptomDiary:
        return SymptomDiaryPage(
          themeController: _themeController,
          authSession: _authSession,
          symptomApiService: _ownedDependencies?.symptomApiService,
          profileApiService: _ownedDependencies?.profileApiService,
        );
      case AppPage.medicationPlan:
        return MedicationPlanPage(
          themeController: _themeController,
          apiClient: _ownedDependencies?.apiClient,
          authSession: _authSession,
        );
      case AppPage.home:
        return _buildHomeScreen();
    }
  }

  Widget _buildUnauthenticatedPage(AppPage page) {
    switch (page) {
      case AppPage.login:
        return LoginScreen(
          chatController: _chatController,
          themeController: _themeController,
          authSession: _authSession,
          authApiService: _authApiService,
          symptomRepository: _symptomRepository,
        );
      case AppPage.registration:
        return RegistrationScreen(
          chatController: _chatController,
          themeController: _themeController,
          authSession: _authSession,
          authApiService: _authApiService,
          symptomRepository: _symptomRepository,
        );
      case AppPage.onboarding:
      case AppPage.home:
      case AppPage.chat:
      case AppPage.calendar:
      case AppPage.history:
      case AppPage.settings:
      case AppPage.documents:
      case AppPage.appointments:
      case AppPage.symptomDiary:
      case AppPage.medicationPlan:
        return _buildOnboardingScreen();
    }
  }

  OnboardingScreen _buildOnboardingScreen() {
    return OnboardingScreen(
      chatController: _chatController,
      themeController: _themeController,
      authSession: _authSession,
      authApiService: _authApiService,
      symptomRepository: _symptomRepository,
    );
  }

  HomeScreen _buildHomeScreen() {
    return HomeScreen(
      controller: _chatController,
      themeController: _themeController,
      apiClient: _ownedDependencies?.apiClient,
      authSession: _authSession,
      authApiService: _authApiService,
      symptomApiService: _ownedDependencies?.symptomApiService,
    );
  }
}

class _InitialAppState {
  final bool isAuthenticated;
  final AppPage? currentPage;

  const _InitialAppState({
    required this.isAuthenticated,
    required this.currentPage,
  });
}
