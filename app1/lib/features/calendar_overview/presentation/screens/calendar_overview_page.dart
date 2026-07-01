import 'package:app1/app/app_dependencies_scope.dart';
import 'package:app1/app/app_page_store.dart';
import 'package:app1/app/app_navigation_fallbacks.dart';
import 'package:app1/core/network/api_client.dart';
import 'package:app1/core/themes/theme_controller.dart';
import 'package:app1/core/widgets/careena_info_card.dart';
import 'package:app1/core/widgets/careena_page_header.dart';
import 'package:app1/core/widgets/careena_snack_bar.dart';
import 'package:app1/core/widgets/responsive_frame.dart';
import 'package:app1/features/appointmentscreen/controllers/appointment_controller.dart';
import 'package:app1/features/appointmentscreen/data/models/appointment.dart';
import 'package:app1/features/appointmentscreen/presentation/screens/appointment_screen.dart';
import 'package:app1/features/appointmentscreen/presentation/widgets/appointment_profile_filter.dart';
import 'package:app1/features/authscreen/state/auth_session.dart';
import 'package:app1/features/calendar_overview/presentation/utils/calendar_overview_date_utils.dart';
import 'package:app1/features/calendar_overview/presentation/widgets/calendar_day_overview.dart';
import 'package:app1/features/calendar_overview/presentation/widgets/calendar_month_grid.dart';
import 'package:app1/features/calendar_overview/presentation/widgets/calendar_month_header.dart';
import 'package:app1/features/chatscreen/presentation/screens/chat_history_screen.dart';
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
  late int? _selectedProfileId;
  bool _showAllProfiles = false;
  final Set<int> _loadedRemoteAppointmentProfileIds = {};
  final Set<int> _loadingRemoteAppointmentProfileIds = {};
  AuthSession? _observedAuthSession;
  int? _lastActiveProfileId;

  @override
  void initState() {
    super.initState();
    AppPageStore.saveCurrentPage(AppPage.calendar);
    final now = DateTime.now();
    _today = DateTime(now.year, now.month, now.day);
    _focusedMonth = DateTime(_today.year, _today.month);
    _selectedDate = _today;
    _selectedProfileId = widget.authSession?.activeProfileId;
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
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;
      _loadEntries();
    });
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _syncAuthSessionListener();
  }

  @override
  void didUpdateWidget(covariant CalendarOverviewPage oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (!identical(oldWidget.authSession, widget.authSession)) {
      _syncAuthSessionListener();
    }
  }

  @override
  void dispose() {
    _observedAuthSession?.removeListener(_handleAuthSessionChanged);
    _appointmentController.dispose();
    super.dispose();
  }

  void _syncAuthSessionListener() {
    final nextSession = _currentAuthSession();

    if (identical(nextSession, _observedAuthSession)) {
      return;
    }

    _observedAuthSession?.removeListener(_handleAuthSessionChanged);
    _observedAuthSession = nextSession;
    _lastActiveProfileId = nextSession?.activeProfileId;

    if (!_showAllProfiles) {
      _selectedProfileId = _lastActiveProfileId;
    }

    _observedAuthSession?.addListener(_handleAuthSessionChanged);
  }

  void _handleAuthSessionChanged() {
    final nextProfileId = _observedAuthSession?.activeProfileId;

    if (nextProfileId == _lastActiveProfileId) {
      if (mounted) {
        setState(() {});
      }
      return;
    }

    _lastActiveProfileId = nextProfileId;
    if (!mounted) return;

    if (_showAllProfiles) {
      setState(() {});
      return;
    }

    setState(() {
      _selectedProfileId = nextProfileId;
      _isLoading = true;
    });
    _loadEntries();
  }

  AuthSession? _currentAuthSession() {
    return widget.authSession ??
        AppDependenciesScope.maybeOf(context)?.authSession;
  }

  Future<void> _loadEntries() async {
    final symptoms = await _loadSymptomsForCurrentProfileView();
    final medications = await _loadMedicationsForCurrentProfileView();
    await _loadRecommendedAppointmentsForCurrentProfileView(
      refreshAfterLoad: false,
    );
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
    final authSession = _currentAuthSession();
    final activeProfile = authSession?.activeProfile;
    final canViewAllProfiles =
        activeProfile?.profileType == 'self' || activeProfile?.role == 'owner';

    return Scaffold(
      appBar: CareenaPageHeader(title: 'Kalender', onBack: _openHome),
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
                  const CareenaInfoCard(
                    text:
                        'Sieh Termine, Symptome und Medikamente in einer gemeinsamen Monatsübersicht.',
                  ),
                  const SizedBox(height: 14),
                  if (canViewAllProfiles) ...[
                    AppointmentProfileFilter(
                      profiles: authSession?.profiles ?? const [],
                      selectedProfileId: _selectedProfileId,
                      showAllProfiles: _showAllProfiles,
                      onShowAll: _showAllProfilesInCalendar,
                      onProfileSelected: _showProfileInCalendar,
                    ),
                    if ((authSession?.profiles.length ?? 0) > 1)
                      const SizedBox(height: 12),
                  ],
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
      return appointmentDate != null &&
          _appointmentMatchesProfileView(appointment) &&
          isSameCalendarDay(appointmentDate, date);
    }).toList();
  }

  List<SymptomEntry> _symptomsForDate(DateTime date) {
    return _symptoms
        .where((entry) => isSameCalendarDay(entry.date, date))
        .toList();
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
    navigateToHomeFallback(context, themeController: widget.themeController);
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
          authSession: widget.authSession ??
              AppDependenciesScope.maybeOf(context)?.authSession,
          initialAppointmentId: appointment.id,
        ),
      ),
    );
  }

  Future<List<SymptomEntry>> _loadSymptomsForCurrentProfileView() async {
    final dependencies = AppDependenciesScope.maybeOf(context);
    final apiService = dependencies?.symptomApiService;
    final authSession = _currentAuthSession();
    final profileIds = _profileIdsForCurrentViewOrSelected(authSession);

    if (profileIds.isEmpty) {
      return const [];
    }

    if (apiService == null ||
        authSession == null ||
        !authSession.isAuthenticated) {
      return _loadLocalSymptomsForProfileIds(profileIds);
    }

    try {
      final responsesByProfile = await Future.wait(
        profileIds.map(
          (profileId) => apiService.getSymptoms(profileId: profileId),
        ),
      );
      return responsesByProfile
          .expand((responses) => responses.map(SymptomEntry.fromResponse))
          .toList()
        ..sort((a, b) => b.date.compareTo(a.date));
    } catch (_) {
      return _loadLocalSymptomsForProfileIds(profileIds);
    }
  }

  Future<List<SymptomEntry>> _loadLocalSymptomsForProfileIds(
    List<int> profileIds,
  ) async {
    final entriesByProfile = await Future.wait(
      profileIds.map((profileId) {
        return _symptomRepository.loadEntries(profileId: profileId);
      }),
    );

    return entriesByProfile.expand((entries) => entries).toList()
      ..sort((a, b) => b.date.compareTo(a.date));
  }

  Future<List<MedicationEntry>> _loadMedicationsForCurrentProfileView() async {
    final dependencies = AppDependenciesScope.maybeOf(context);
    final apiClient = widget.apiClient ?? dependencies?.apiClient;
    final authSession = _currentAuthSession();

    if (apiClient == null || authSession == null || !authSession.isAuthenticated) {
      return _medicationRepository.loadEntries();
    }

    final profileIds = _profileIdsForCurrentView(authSession);
    if (profileIds.isEmpty) {
      return _medicationRepository.loadEntries();
    }

    final apiService = MedicationApiService(apiClient);

    try {
      final entriesByProfile = await Future.wait(
        profileIds.map(apiService.getMedications),
      );
      return entriesByProfile.expand((entries) => entries).toList();
    } catch (_) {
      return _medicationRepository.loadEntries();
    }
  }

  Future<void> _loadRecommendedAppointmentsForCurrentProfileView({
    bool refreshAfterLoad = true,
  }) async {
    final dependencies = AppDependenciesScope.maybeOf(context);
    final authSession = _currentAuthSession();

    if (dependencies == null || authSession == null || !authSession.isAuthenticated) {
      return;
    }

    final profileIds = _profileIdsForCurrentView(authSession);
    await Future.wait(
      profileIds.map(
        (profileId) => _loadRecommendedAppointmentsForProfile(
          profileId,
          refreshAfterLoad: refreshAfterLoad,
        ),
      ),
    );
  }

  Future<void> _loadRecommendedAppointmentsForProfile(
    int profileId, {
    bool refreshAfterLoad = true,
  }) async {
    final dependencies = AppDependenciesScope.maybeOf(context);

    if (dependencies == null ||
        _loadedRemoteAppointmentProfileIds.contains(profileId) ||
        _loadingRemoteAppointmentProfileIds.contains(profileId)) {
      return;
    }

    _loadingRemoteAppointmentProfileIds.add(profileId);

    try {
      final appointments = await dependencies.appointmentApiService
          .getRecommendedAppointments(profileId: profileId);
      _appointmentController.upsertRecommendedAppointments(appointments);
      _loadedRemoteAppointmentProfileIds.add(profileId);
    } catch (_) {
      // Calendar appointments remain readable from local state if the API fails.
    } finally {
      _loadingRemoteAppointmentProfileIds.remove(profileId);
      if (refreshAfterLoad && mounted) {
        setState(() {});
      }
    }
  }

  List<int> _profileIdsForCurrentView(AuthSession authSession) {
    if (_showAllProfiles) {
      return authSession.profiles.map((profile) => profile.id).toSet().toList();
    }

    final profileId = _selectedProfileId ?? authSession.activeProfileId;
    return profileId == null ? const [] : [profileId];
  }

  List<int> _profileIdsForCurrentViewOrSelected(AuthSession? authSession) {
    if (authSession != null) {
      return _profileIdsForCurrentView(authSession);
    }

    final profileId = _selectedProfileId;
    return profileId == null ? const [] : [profileId];
  }

  bool _appointmentMatchesProfileView(Appointment appointment) {
    if (_showAllProfiles) {
      return true;
    }

    final profileId = _selectedProfileId;
    if (profileId == null) {
      return true;
    }

    return appointment.profileId == profileId;
  }

  void _showAllProfilesInCalendar() {
    setState(() {
      _showAllProfiles = true;
      _isLoading = true;
    });
    _loadEntries();
  }

  void _showProfileInCalendar(int profileId) {
    final authSession = _currentAuthSession();
    final profileIsAvailable =
        authSession?.profiles.any((profile) => profile.id == profileId) ?? false;

    if (authSession != null &&
        profileIsAvailable &&
        authSession.activeProfileId != profileId) {
      setState(() {
        _selectedProfileId = profileId;
        _showAllProfiles = false;
        _isLoading = true;
      });
      authSession.setActiveProfileById(profileId);
      return;
    }

    setState(() {
      _selectedProfileId = profileId;
      _showAllProfiles = false;
      _isLoading = true;
    });
    _loadEntries();
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
          profileApiService: dependencies?.profileApiService,
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
    showCareenaSnackBar(context, 'Dieser Bereich ist aktuell nicht verfügbar.');
  }
}
