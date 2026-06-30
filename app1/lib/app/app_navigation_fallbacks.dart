import 'package:app1/app/app_dependencies_scope.dart';
import 'package:app1/core/themes/theme_controller.dart';
import 'package:app1/features/homescreen/presentation/screens/home_screen.dart';
import 'package:flutter/material.dart';

/// Opens Home even when a page was restored as the root route after reload.
void navigateToHomeFallback(
  BuildContext context, {
  required ThemeController? themeController,
}) {
  final dependencies = AppDependenciesScope.maybeOf(context);

  if (dependencies == null || themeController == null) {
    Navigator.of(context).popUntil((route) => route.isFirst);
    return;
  }

  Navigator.of(context, rootNavigator: true).pushAndRemoveUntil(
    MaterialPageRoute(
      builder: (context) => HomeScreen(
        controller: dependencies.chatController,
        themeController: themeController,
        apiClient: dependencies.apiClient,
        authSession: dependencies.authSession,
        authApiService: dependencies.authApiService,
        symptomApiService: dependencies.symptomApiService,
      ),
    ),
    (route) => false,
  );
}