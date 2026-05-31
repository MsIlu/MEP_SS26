import 'package:flutter/material.dart';
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
    return _AppDependencyScope(externalChatController: chatController);
  }
}

/// Keeps long-lived dependencies out of widget build methods.
class _AppDependencyScope extends StatefulWidget {
  final ChatController? externalChatController;

  const _AppDependencyScope({this.externalChatController});

  @override
  State<_AppDependencyScope> createState() => _AppDependencyScopeState();
}

class _AppDependencyScopeState extends State<_AppDependencyScope> {
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
    return AnimatedBuilder(
      animation: _themeController,
      builder: (context, _) {
        return MaterialApp(
          debugShowCheckedModeBanner: false,
          title: 'Careena',
          theme: AppTheme.lightTheme,
          darkTheme: AppTheme.darkTheme,
          themeMode: _themeController.themeMode,
          home: OnboardingScreen(
            chatController: _chatController,
            themeController: _themeController,
          ),
        );
      },
    );
  }
}