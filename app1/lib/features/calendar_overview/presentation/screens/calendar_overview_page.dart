import 'package:app1/app/app_dependencies_scope.dart';
import 'package:app1/core/network/api_client.dart';
import 'package:app1/core/themes/theme_controller.dart';
import 'package:app1/core/widgets/careena_page_header.dart';
import 'package:app1/core/widgets/responsive_frame.dart';
import 'package:app1/features/appointmentscreen/controllers/appointment_controller.dart';
import 'package:app1/features/appointmentscreen/data/models/appointment.dart';
import 'package:app1/features/appointmentscreen/presentation/screens/appointment_screen.dart';
import 'package:app1/features/authscreen/state/auth_session.dart';
import 'package:app1/features/calendar_overview/presentation/utils/calendar_overview_date_utils.dart';
import 'package:app1/features/calendar_overview/presentation/widgets/calendar_day_overview.dart';
import 'package:app1/features/calendar_overview/presentation/widgets/calendar_month_grid.dart';
import 'package:app1/features/calendar_overview/presentation/widgets/calendar_month_header.dart';
import 'package:app1/features/chatscreen/presentation/screens/chat_history_screen.dart';
import 'package:app1/features/homescreen/presentation/screens/home_screen.dart';
import 'package:app1/features/homescreen/presentation/widgets/custom_bottom_nav.dart';
import 'package:app1/features/medication_plan/data/medication_api_service.dart';
import 'package:app1/features/medication_plan/data/medication_entry.dart';
import 'package:app1/features/medication_plan/data/medication_repository.dart';
import 'package:app1/features/medication_plan/presentation/screens/medication_plan_page.dart';
import 'package:app1/features/medication_plan/presentation/utils/medication_plan_builder.dart';
import 'package:app1/features/settings/presentation/screens/settings_page.dart';
import 'package:app1/features/symptom_diary/data/symptom_entry.dart';
import 'package:app1/features/symptom_diary/data/symptom_repository.dart';
import 'package:app1/features/symptom_diary/presentation/screens/symptom_diary_page.dart';
import 'package:flutter/material.dart';

/// Coordinates calendar data loading, filtering, and navigation.
class CalendarOverviewPage extends StatefulWidget {
  final ThemeController? themeController;
  final ApiClient? apiClient;
  final AuthSession? authSession;
  final AppointmentController? appointmentController;
  final SymptomRepository? symptomRepository;
  final MedicationRepository? medicationRepository;

  const CalendarOverviewPage({
    super.key,
    this.themeController,
    this.apiClient,
    this.authSession,
    this.appointmentController,
    this.symptomRepository,
    this.medicationRepository,
  });

  @override
  State<CalendarOverviewPage> createState() => _CalendarOverviewPageState();
}

class _CalendarOverviewPageState extends State<CalendarOverviewPage> {
  late final AppointmentController _appointmentController;
  late final SymptomRepository _symptomRepository;
  late final MedicationRepository _medicationRepository;
  late final DateTime _today;
  late DateTime _focusedMonth;
  late DateTime _selectedDate;
  List<SymptomEntry> _symptoms = const [];
  List<MedicationEntry> _medications = const [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    final now = DateTime.now();
    _today = DateTime(now.year, now.month, now.day);
    _focusedMonth = DateTime(_today.year, _today.month);
    _selectedDate = _today;
    _appointmentController =
        widget.appointmentController ?? AppointmentController();
    _symptomRepository = widget.symptomRepository ?? SymptomRepository();
    _medicationRepository =
        widget.medicationRepository ??
        MedicationRepository(
          apiService: widget.apiClient == null
              ? null
              : MedicationApiService(widget.apiClient!),
          profileId: widget.authSession?.activeProfileId,
        );
    _loadEntries();
  }

  @override
  void dispose() {
    _appointmentController.dispose();
    super.dispose();
  }

  Future<void> _loadEntries() async {
    final symptoms = await _symptomRepository.loadEntries();
    final medications = await _medicationRepository.loadEntries();
    if (!mounted) return;

    setState(() {
      _symptoms = symptoms;
      _medications = medications;
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    final simpleView = widget.themeController?.isSimpleView ?? false;

    return Scaffold(
      appBar: CareenaPageHeader(
        title: 'Kalender',
        trailing: widget.themeController == null
            ? null
            : CareenaThemeHeaderAction(
                onPressed: widget.themeController!.toggleTheme,
                isDarkMode: widget.themeController!.isDarkMode,
              ),
      ),
      body: SafeArea(
        child: AnimatedBuilder(
          animation: _appointmentController.appointments,
          builder: (context, _) {
            return ResponsivePageBody(
              maxWidth: 760,
              scrollable: true,
              padding: const EdgeInsets.fromLTRB(18, 18, 18, 96),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  CalendarMonthHeader(
                    month: _focusedMonth,
                    onPrevious: () => _shiftMonth(-1),
                    onNext: () => _shiftMonth(1),
                  ),
                  const SizedBox(height: 12),
                  CalendarMonthGrid(
                    focusedMonth: _focusedMonth,
                    selectedDate: _selectedDate,
                    today: _today,
                    hasItems: _hasItemsForDate,
                    onSelected: _selectDate,
                  ),
                  const SizedBox(height: 18),
                  if (_isLoading)
                    const Center(child: CircularProgressIndicator())
                  else
                    CalendarDayOverview(
                      date: _selectedDate,
                      appointments: _appointmentsForDate(_selectedDate),
                      symptoms: _symptomsForDate(_selectedDate),
                      medications: plannedMedicationDosesForDate(
                        _medications,
                        _selectedDate,
                      ),
                      onAppointmentTap: _openAppointment,
                      onSymptomTap: _openSymptom,
                      onMedicationTap: _openMedication,
                    ),
                ],
              ),
            );
          },
        ),
      ),
      bottomNavigationBar: CustomBottomNav(
        // Calendar is the second primary destination in the shared app nav.
        currentIndex: 1,
        isSimpleView: simpleView,
        onTap: _onBottomNavigationTap,
      ),
    );
  }

  void _shiftMonth(int delta) {
    setState(() {
      _focusedMonth = DateTime(_focusedMonth.year, _focusedMonth.month + delta);
      _selectedDate = DateTime(_focusedMonth.year, _focusedMonth.month, 1);
    });
  }

  void _selectDate(DateTime date) {
    setState(() => _selectedDate = date);
  }

  bool _hasItemsForDate(DateTime date) {
    return _appointmentsForDate(date).isNotEmpty ||
        _symptomsForDate(date).isNotEmpty ||
        plannedMedicationDosesForDate(_medications, date).isNotEmpty;
  }

  List<Appointment> _appointmentsForDate(DateTime date) {
    return _appointmentController.appointments.value.where((appointment) {
      final appointmentDate = appointment.appointmentDate;
      return appointmentDate != null && isSameCalendarDay(appointmentDate, date);
    }).toList();
  }

  List<SymptomEntry> _symptomsForDate(DateTime date) {
    return _symptoms.where((entry) => isSameCalendarDay(entry.date, date)).toList();
  }

  void _onBottomNavigationTap(int index) {
    if (index == 1) return;
    if (index == 0) {
      _openHome();
      return;
    }

    final dependencies = AppDependenciesScope.maybeOf(context);
    final themeController = widget.themeController;
    if (themeController == null) {
      _showNavigationUnavailable();
      return;
    }

    if (index == 2) {
      final activeProfileId = dependencies?.authSession.activeProfileId;
      if (dependencies == null || activeProfileId == null) {
        _showNavigationUnavailable();
        return;
      }

      Navigator.of(context).pushReplacement(
        MaterialPageRoute(
          builder: (context) => ChatHistoryScreen(
            themeController: themeController,
            profileId: activeProfileId,
            repository: dependencies.chatController.chatHistoryRepository,
          ),
        ),
      );
      return;
    }

    if (index == 3) {
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(
          builder: (context) => SettingsPage(
            themeController: themeController,
            authSession: dependencies?.authSession,
            authApiService: dependencies?.authApiService,
            profileApiService: dependencies?.profileApiService,
          ),
        ),
      );
    }
  }

  void _openHome() {
    final dependencies = AppDependenciesScope.maybeOf(context);
    final themeController = widget.themeController;
    if (dependencies == null || themeController == null) {
      // Isolated widget tests already have the home route below the calendar.
      Navigator.of(context).popUntil((route) => route.isFirst);
      return;
    }

    Navigator.of(context).pushAndRemoveUntil(
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

  void _openAppointment(Appointment appointment) {
    final themeController = widget.themeController;
    if (themeController == null) {
      _showNavigationUnavailable();
      return;
    }

    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => AppointmentScreen(
          themeController: themeController,
          initialAppointmentId: appointment.id,
        ),
      ),
    );
  }

  void _openSymptom(SymptomEntry entry) {
    final dependencies = AppDependenciesScope.maybeOf(context);
    final themeController = widget.themeController;
    if (themeController == null) {
      _showNavigationUnavailable();
      return;
    }

    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => SymptomDiaryPage(
          themeController: themeController,
          authSession: widget.authSession ?? dependencies?.authSession,
          symptomApiService: dependencies?.symptomApiService,
          initialDate: entry.date,
        ),
      ),
    );
  }

  void _openMedication(MedicationEntry entry) {
    final dependencies = AppDependenciesScope.maybeOf(context);
    final themeController = widget.themeController;
    if (themeController == null) {
      _showNavigationUnavailable();
      return;
    }

    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => MedicationPlanPage(
          themeController: themeController,
          apiClient: widget.apiClient ?? dependencies?.apiClient,
          authSession: widget.authSession ?? dependencies?.authSession,
          initialMedicationId: entry.id,
          initialDate: _selectedDate,
        ),
      ),
    );
  }

  void _showNavigationUnavailable() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Dieser Bereich ist aktuell nicht verfügbar.')),
    );
  }
}
