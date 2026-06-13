import 'package:app1/features/chatscreen/controllers/chat_controller.dart';
import 'package:app1/features/chatscreen/presentation/screens/chat_screen.dart';
import 'package:app1/features/medication_plan/presentation/screens/medication_plan_page.dart';
import 'package:app1/features/symptom_diary/presentation/screens/symptom_diary_page.dart';
import 'package:app1/features/settings/presentation/screens/settings_page.dart';
import 'package:app1/features/authscreen/data/auth_api_service.dart';
import 'package:app1/features/authscreen/state/auth_session.dart';
import 'package:flutter/material.dart';
import 'package:app1/app/app_dependencies_scope.dart';
import 'package:app1/core/themes/app_colors.dart';
import 'package:app1/core/network/api_client.dart';
import 'package:app1/features/authscreen/state/auth_session.dart';
import '../../../../core/widgets/responsive_frame.dart';
import '../../../../core/widgets/careena_page_header.dart';
import '../../data/home_feature.dart';
import '../widgets/careena_hero_card.dart';
import '../widgets/custom_bottom_nav.dart';
import '../widgets/home_function_list.dart';
import '../widgets/home_search_bar.dart';
import '../../../../core/themes/theme_controller.dart';

/// Dashboard-style home screen with the Careena entry point and feature list.
class HomeScreen extends StatelessWidget {
  /// Shared chat controller reused when opening the chat from the home screen.
  final ChatController controller;

  /// Shared theme controller used to switch between light and dark mode.
  final ThemeController themeController;
  final ApiClient? apiClient;
  final AuthSession? authSession;
  final AuthApiService? authApiService;

  const HomeScreen({
    super.key,
    required this.controller,
    required this.themeController,
    this.apiClient,
    this.authSession,
    this.authApiService,
  });

  @override
  Widget build(BuildContext context) {
    final features = _buildFeatures(context);
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    // A very small width needs tighter horizontal spacing than the shared
    // breakpoint helpers, because this screen has several fixed-size elements.
    final isCompact = MediaQuery.sizeOf(context).width < 360;

    return Scaffold(
      backgroundColor: isDarkMode
          ? Theme.of(context).scaffoldBackgroundColor
          : AppColors.headerBackgroundLight,
      appBar: CareenaPageHeader(
        title: 'Willkommen!',
        showBack: false,
        trailing: themeController.isSimpleView
            ? null
            : CareenaThemeHeaderAction(
                onPressed: themeController.toggleTheme,
                isDarkMode: themeController.isDarkMode,
              ),
      ),
      body: SafeArea(
        child: ResponsivePageBody(
          maxWidth: 720,
          child: Column(
            children: [
              CareenaHeroCard(
                onTap: () => _navigateToChat(context),
                isSimpleView: themeController.isSimpleView,
              ),
              if (!themeController.isSimpleView)
                HomeSearchBar(isCompact: isCompact),
              HomeFunctionList(
                features: features,
                isSimpleView: themeController.isSimpleView,
              ),
            ],
          ),
        ),
      ),
      bottomNavigationBar: CustomBottomNav(
        isSimpleView: themeController.isSimpleView,
        onTap: (index) => _onBottomNavigationTap(context, index),
      ),
    );
  }

  void _onBottomNavigationTap(BuildContext context, int index) {
    if (themeController.isSimpleView && index == 1) {
      _openSettings(context);
      return;
    }

    if (index == 2) {
      _navigateToChat(context);
    } else if (index == 3) {
      _openSettings(context);
    }
  }

  void _openSettings(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => SettingsPage(
          themeController: themeController,
          authSession: authSession,
          authApiService: authApiService,
        ),
      ),
    );
  }

  /// Navigates to the chat while preserving the existing controller instance.
  void _navigateToChat(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => ChatScreen(
          controller: controller,
          themeController: themeController,
        ),
      ),
    );
  }

  /// Defines the currently available home features.
  List<HomeFeature> _buildFeatures(BuildContext context) {
    const featureColor = AppColors.careenaInfoBorder;

    return [
      HomeFeature(
        icon: Icons.access_time,
        title: "Terminplanung",
        backgroundColor: featureColor,
        onTap: () {},
      ),
      HomeFeature(
        icon: Icons.medication,
        title: "Medikamentenplan",
        backgroundColor: featureColor,
        onTap: () => _navigateToMedicationPlan(context),
      ),
      HomeFeature(
        icon: Icons.description_outlined,
        title: "Dokumente",
        backgroundColor: featureColor,
        onTap: () {},
      ),
      HomeFeature(
        icon: Icons.health_and_safety_outlined,
        title: "Präventive Angebote",
        backgroundColor: featureColor,
        onTap: () {},
      ),
      HomeFeature(
        icon: Icons.menu_book_outlined,
        title: "Symptomtagebuch",
        backgroundColor: featureColor,
        onTap: () => _navigateToSymptomDiary(context),
      ),
    ];
  }

  void _navigateToMedicationPlan(BuildContext context) {
    final dependencies = _dependenciesFromContext(context);

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => MedicationPlanPage(
          themeController: themeController,
          apiClient: apiClient ?? dependencies?.dependencies.apiClient,
          authSession: authSession ?? dependencies?.dependencies.authSession,
        ),
      ),
    );
  }

  void _navigateToSymptomDiary(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) =>
            SymptomDiaryPage(themeController: themeController),
      ),
    );
  }
  AppDependenciesScope? _dependenciesFromContext(BuildContext context) {
    return context
            .getElementForInheritedWidgetOfExactType<AppDependenciesScope>()
            ?.widget
        as AppDependenciesScope?;
  }
}
