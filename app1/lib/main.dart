import 'package:app1/app/app_dependencies_scope.dart';
import 'package:app1/features/symptom_diary/data/symptom_repository.dart';
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
    return _AppBoot(
      externalChatController: chatController,
      externalAuthApiService: authApiService,
    );
  }
}


class _AppBoot extends StatefulWidget {
  final ChatController? externalChatController;
  final AuthApiService? externalAuthApiService;

  const _AppBoot({
    this.externalChatController,
    this.externalAuthApiService,
  });

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
    return AppDependenciesScope(
      dependencies: _ownedDependencies!, 
      child: AnimatedBuilder(
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
              symptomRepository: _symptomRepository,
            ),
          );
        },
      ),
    );
  }
}