import 'package:app1/app/app_dependencies_scope.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'app/app_dependencies.dart';
import 'core/themes/app_theme.dart';
import 'core/themes/theme_controller.dart';
import 'features/chatscreen/controllers/chat_controller.dart';
import 'features/onboardingscreen/presentation/screens/onboarding_screen.dart';

void main() {
  runApp(const MyApp());
}

/// Root widget for the Careena app.
class MyApp extends StatelessWidget {
  final ChatController? chatController;

  const MyApp({super.key, this.chatController});

  @override
  Widget build(BuildContext context) {
    return AppBoot(externalChatController: chatController);
  }
}


class AppBoot extends StatefulWidget {
  final ChatController? externalChatController;

  const AppBoot({this.externalChatController});

  @override
  State<AppBoot> createState() => AppBootState();
}

class AppBootState extends State<AppBoot> {
  late final AppDependencies? _ownedDependencies;
  late final ChatController _chatController;
  late final ThemeController _themeController;

  @override
  void initState() {
    super.initState();

    _ownedDependencies = widget.externalChatController == null
        ? AppDependencies()
        : null;

    _chatController =
        widget.externalChatController ?? _ownedDependencies!.chatController;

    _themeController = ThemeController();
  }

  @override
  void dispose() {
    _themeController.dispose();
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
            ),
          );
        },
      ),
    );
  }
}