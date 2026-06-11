import 'package:app1/features/chatscreen/controllers/chat_controller.dart';
import 'package:app1/features/chatscreen/presentation/screens/chat_screen.dart';
import 'package:app1/features/medication_plan/presentation/screens/medication_plan_page.dart';
import 'package:app1/features/symptom_diary/presentation/screens/symptom_diary_page.dart';
import '../../../appointmentscreen/presentation/screens/appointment_screen.dart';
import 'package:flutter/material.dart';
import 'package:app1/core/themes/app_colors.dart';
import '../../../../core/widgets/responsive_frame.dart';
import '../../data/home_feature.dart';
import '../widgets/careena_hero_card.dart';
import '../widgets/custom_bottom_nav.dart';
import '../widgets/home_function_list.dart';
import '../widgets/home_header.dart';
import '../widgets/home_search_bar.dart';
import '../../../../core/themes/theme_controller.dart';

/// Dashboard-style home screen with the Careena entry point and feature list.
class HomeScreen extends StatelessWidget {
  /// Shared chat controller reused when opening the chat from the home screen.
  final ChatController controller;

  /// Shared theme controller used to switch between light and dark mode.
  final ThemeController themeController; 

  const HomeScreen({
    super.key,
    required this.controller,
    required this.themeController,
  });

  @override
  Widget build(BuildContext context) {
    final features = _buildFeatures(context);
    // A very small width needs tighter horizontal spacing than the shared
    // breakpoint helpers, because this screen has several fixed-size elements.
    final isCompact = MediaQuery.sizeOf(context).width < 360;

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      body: SafeArea(
        child: ResponsivePageBody(
          maxWidth: 720,
          child: Column(
            children: [
              HomeHeader(
                isCompact: isCompact,
                onToggleTheme: themeController.toggleTheme,
                isDarkMode: themeController.isDarkMode,
              ),
              CareenaHeroCard(onTap: () => _navigateToChat(context)),
              HomeSearchBar(isCompact: isCompact),
              HomeFunctionList(features: features),
            ],
          ),
        ),
      ),
      bottomNavigationBar: const CustomBottomNav(),
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
        onTap: () => _navigateToAppointments(context),
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
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) =>
            MedicationPlanPage(themeController: themeController),
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

  void _navigateToAppointments(BuildContext context) {
  Navigator.push(
    context,
    MaterialPageRoute(
      builder: (context) => AppointmentScreen(),
),
  );
}
}