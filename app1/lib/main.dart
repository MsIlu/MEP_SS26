import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'app/app_dependencies.dart';
import 'core/themes/app_theme.dart';
import 'core/themes/theme_controller.dart';
import 'features/chatscreen/controllers/chat_controller.dart';
import 'features/onboardingscreen/presentation/screens/onboarding_screen.dart';
import 'features/authscreen/state/auth_session.dart';
import 'features/authscreen/data/auth_api_service.dart';

void main() {
  runApp(const MyApp());
}

/// Root widget for the Careena app.
class MyApp extends StatelessWidget {
  final ChatController? chatController;
  final AuthApiService? authApiService;

  const MyApp({
    super.key,
    this.chatController,
    this.authApiService,
  });

  @override
  Widget build(BuildContext context) {
    return _AppDependencyScope(
      externalChatController: chatController,
      externalAuthApiService: authApiService,
    );
  }
}

/// Keeps long-lived dependencies out of widget build methods.
class _AppDependencyScope extends StatefulWidget {
  final ChatController? externalChatController;
  final AuthApiService? externalAuthApiService;

  const _AppDependencyScope({
    this.externalChatController,
    this.externalAuthApiService,
  });

  @override
  State<_AppDependencyScope> createState() => _AppDependencyScopeState();
}

class _AppDependencyScopeState extends State<_AppDependencyScope> {
  late final AppDependencies? _ownedDependencies;
  late final ChatController _chatController;
  late final ThemeController _themeController;
  late final AuthSession _authSession;
  late final AuthApiService _authApiService;

  @override
  void initState() {
    super.initState();

    _authSession = AuthSession();

    _ownedDependencies =
    widget.externalChatController == null &&
        widget.externalAuthApiService == null
        ? AppDependencies(authSession: _authSession)
        : null;

    _chatController =
        widget.externalChatController ?? _ownedDependencies!.chatController;

    _authApiService =
        widget.externalAuthApiService ?? _ownedDependencies!.authApiService;

    _themeController = ThemeController();
  }

  @override
  void dispose() {
    _themeController.dispose();
    _authSession.dispose();
    _ownedDependencies?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _themeController,
      builder: (context, _) {
        return MaterialApp(
          debugShowCheckedModeBanner: false,
          title: 'Careena',
          locale: const Locale('de', 'DE'),
          supportedLocales: const [Locale('de', 'DE')],
          localizationsDelegates: GlobalMaterialLocalizations.delegates,
          theme: AppTheme.lightTheme,
          darkTheme: AppTheme.darkTheme,
          themeMode: _themeController.themeMode,
          home: OnboardingScreen(
            chatController: _chatController,
            themeController: _themeController,
            authSession: _authSession,
            authApiService: _authApiService,
          ),
        );
      },
    );
  }
}