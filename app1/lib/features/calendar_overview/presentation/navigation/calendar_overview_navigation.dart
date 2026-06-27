import 'package:app1/app/app_dependencies_scope.dart';
import 'package:app1/core/network/api_client.dart';
import 'package:app1/core/themes/theme_controller.dart';
import 'package:app1/core/widgets/careena_snack_bar.dart';
import 'package:app1/features/appointmentscreen/data/models/appointment.dart';
import 'package:app1/features/appointmentscreen/presentation/screens/appointment_screen.dart';
import 'package:app1/features/authscreen/state/auth_session.dart';
import 'package:app1/features/chatscreen/presentation/screens/chat_history_screen.dart';
import 'package:app1/features/homescreen/presentation/screens/home_screen.dart';
import 'package:app1/features/medication_plan/data/medication_entry.dart';
import 'package:app1/features/medication_plan/presentation/screens/medication_plan_page.dart';
import 'package:app1/features/settings/presentation/screens/settings_page.dart';
import 'package:app1/features/symptom_diary/data/symptom_entry.dart';
import 'package:app1/features/symptom_diary/presentation/screens/symptom_diary_page.dart';
import 'package:flutter/material.dart';

/// Keeps calendar route decisions out of the overview screen.
class CalendarOverviewNavigation {
  final BuildContext context;
  final ThemeController? themeController;
  final ApiClient? apiClient;
  final AuthSession? authSession;

  const CalendarOverviewNavigation({
    required this.context,
    required this.themeController,
    this.apiClient,
    this.authSession,
  });

  void handleBottomNavigation(int index) {
    if (index == 1) return;
    if (index == 0) {
      openHome();
      return;
    }
    if (!_hasThemeController) return;

    if (index == 2) {
      openHistory();
    } else if (index == 3) {
      openSettings();
    }
  }

  void openHome() {
    final dependencies = AppDependenciesScope.maybeOf(context);
    if (dependencies == null || themeController == null) {
      // Isolated widget tests already have the home route below the calendar.
      Navigator.of(context).popUntil((route) => route.isFirst);
      return;
    }

    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(
        builder: (context) => HomeScreen(
          controller: dependencies.chatController,
          themeController: themeController!,
          apiClient: dependencies.apiClient,
          authSession: dependencies.authSession,
          authApiService: dependencies.authApiService,
          symptomApiService: dependencies.symptomApiService,
        ),
      ),
      (route) => false,
    );
  }

  void openHistory() {
    final dependencies = AppDependenciesScope.maybeOf(context);
    final activeProfileId = dependencies?.authSession.activeProfileId;
    if (dependencies == null || activeProfileId == null || !_hasThemeController) {
      return;
    }

    Navigator.of(context).pushReplacement(
      MaterialPageRoute(
        builder: (context) => ChatHistoryScreen(
          themeController: themeController!,
          profileId: activeProfileId,
          repository: dependencies.chatController.chatHistoryRepository,
        ),
      ),
    );
  }

  void openSettings() {
    final dependencies = AppDependenciesScope.maybeOf(context);
    if (!_hasThemeController) return;

    Navigator.of(context).pushReplacement(
      MaterialPageRoute(
        builder: (context) => SettingsPage(
          themeController: themeController!,
          authSession: dependencies?.authSession,
          authApiService: dependencies?.authApiService,
          profileApiService: dependencies?.profileApiService,
        ),
      ),
    );
  }

  void openAppointment(Appointment appointment) {
    if (!_hasThemeController) return;

    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => AppointmentScreen(
          themeController: themeController,
          initialAppointmentId: appointment.id,
        ),
      ),
    );
  }

  void openSymptom(SymptomEntry entry) {
    final dependencies = AppDependenciesScope.maybeOf(context);
    if (!_hasThemeController) return;

    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => SymptomDiaryPage(
          themeController: themeController!,
          authSession: authSession ?? dependencies?.authSession,
          symptomApiService: dependencies?.symptomApiService,
          profileApiService: dependencies?.profileApiService,
          initialDate: entry.date,
        ),
      ),
    );
  }

  void openMedication(MedicationEntry entry, DateTime selectedDate) {
    final dependencies = AppDependenciesScope.maybeOf(context);
    if (!_hasThemeController) return;

    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => MedicationPlanPage(
          themeController: themeController!,
          apiClient: apiClient ?? dependencies?.apiClient,
          authSession: authSession ?? dependencies?.authSession,
          initialMedicationId: entry.id,
          initialDate: selectedDate,
        ),
      ),
    );
  }

  bool get _hasThemeController {
    if (themeController != null) return true;
    showCareenaSnackBar(context, 'Dieser Bereich ist aktuell nicht verfügbar.');
    return false;
  }
}
