import 'package:app1/app/app_dependencies_scope.dart';
import 'package:app1/app/app_page_store.dart';
import 'package:app1/core/themes/app_colors.dart';
import 'package:app1/app/app_navigation_fallbacks.dart';
import 'package:app1/core/themes/theme_controller.dart';
import 'package:app1/core/widgets/responsive_frame.dart';
import 'package:flutter/material.dart';
import 'package:flutter/semantics.dart';

import '../../../../core/widgets/careena_page_header.dart';
import '../../../../core/widgets/careena_snack_bar.dart';
import '../../controllers/appointment_controller.dart';
import '../../data/models/appointment.dart';
import '../widgets/appointment_116117_card.dart';
import '../widgets/appointment_dialog.dart';
import '../widgets/appointment_filter_bar.dart';
import '../widgets/appointment_info_card.dart';
import '../widgets/appointment_list.dart';
import '../widgets/appointment_profile_filter.dart';
import '../../../authscreen/state/auth_session.dart';
import '../../../recommendation_export/data/appointment_search_api_service.dart';

class AppointmentScreen extends StatefulWidget {
  final ThemeController? themeController;
  final String? initialAppointmentId;
  final AuthSession? authSession;

  const AppointmentScreen({
    super.key,
    this.themeController,
    this.authSession,
    this.initialAppointmentId,
  });

  @override
  State<AppointmentScreen> createState() => _AppointmentScreenState();
}

class _AppointmentScreenState extends State<AppointmentScreen> {
  late int? selectedProfileId = widget.authSession?.activeProfileId;
  final AppointmentController controller = AppointmentController();
  final doctorController = TextEditingController();
  final noteController = TextEditingController();
  final dateController = TextEditingController();
  final timeController = TextEditingController();

  DateTime? selectedDate;
  TimeOfDay? selectedTime;

  bool showAllProfiles = false;
  String selectedFilter = 'Alle';
  final Set<int> _loadedRemoteProfileIds = {};
  final Set<int> _loadingRemoteProfileIds = {};
  AuthSession? _observedAuthSession;
  int? _lastActiveProfileId;

  @override
  void initState() {
    super.initState();
    AppPageStore.saveCurrentPage(AppPage.appointments);
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      if (!mounted) return;
      await _loadRecommendedAppointmentsForCurrentView();
      if (!mounted) return;
      _openInitialAppointment();
    });
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _syncAuthSessionListener();
  }

  @override
  void didUpdateWidget(covariant AppointmentScreen oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (!identical(oldWidget.authSession, widget.authSession)) {
      _syncAuthSessionListener();
    }
  }

  void _syncAuthSessionListener() {
    final nextSession = _currentAuthSession();

    if (identical(nextSession, _observedAuthSession)) {
      return;
    }

    _observedAuthSession?.removeListener(_handleAuthSessionChanged);
    _observedAuthSession = nextSession;
    _lastActiveProfileId = nextSession?.activeProfileId;

    if (!showAllProfiles) {
      selectedProfileId = _lastActiveProfileId;
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

    if (showAllProfiles) {
      setState(() {});
      return;
    }

    setState(() {
      selectedProfileId = nextProfileId;
    });
    _loadRecommendedAppointmentsForCurrentView();
  }

  AuthSession? _currentAuthSession() {
    return widget.authSession ??
        AppDependenciesScope.maybeOf(context)?.authSession;
  }

  void _openInitialAppointment() {
    final appointmentId = widget.initialAppointmentId;
    if (appointmentId == null || !mounted) return;

    for (final appointment in controller.appointments.value) {
      if (appointment.id == appointmentId) {
        _showEditDialog(appointment);
        return;
      }
    }
  }

  Future<void> _loadRecommendedAppointmentsForCurrentView() async {
    final authSession = _currentAuthSession();

    if (showAllProfiles) {
      final profiles = authSession?.profiles ?? const [];
      final profileIds = profiles.map((profile) => profile.id).toSet();

      await Future.wait(profileIds.map(_loadRecommendedAppointmentsForProfile));
      return;
    }

    final profileId = selectedProfileId;
    if (profileId == null) {
      return;
    }

    await _loadRecommendedAppointmentsForProfile(profileId);
  }

  Future<void> _loadRecommendedAppointmentsForProfile(int profileId) async {
    final dependencies = AppDependenciesScope.maybeOf(context);
    final authSession = _currentAuthSession();

    if (dependencies == null ||
        authSession == null ||
        !authSession.isAuthenticated) {
      return;
    }

    if (_loadedRemoteProfileIds.contains(profileId) ||
        _loadingRemoteProfileIds.contains(profileId)) {
      return;
    }

    _loadingRemoteProfileIds.add(profileId);

    try {
      final appointments = await dependencies.appointmentApiService
          .getRecommendedAppointments(profileId: profileId);
      controller.upsertRecommendedAppointments(appointments);
      _loadedRemoteProfileIds.add(profileId);
    } catch (_) {
      // Loading DB-backed appointment recommendations is best-effort.
    } finally {
      _loadingRemoteProfileIds.remove(profileId);
      if (mounted) {
        setState(() {});
      }
    }
  }

  Future<void> _pickDate() async {
    final pickedDate = await showDatePicker(
      context: context,
      initialDate: DateTime.now(),
      firstDate: DateTime.now(),
      lastDate: DateTime(2100),
      helpText: 'Datum auswählen',
      cancelText: 'Abbrechen',
      confirmText: 'OK',
      builder: (context, child) {
        final isDark = Theme.of(context).brightness == Brightness.dark;
        final mediaQuery = MediaQuery.of(context);

        return MediaQuery(
          data: mediaQuery.copyWith(size: const Size(420, 720)),
          child: Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 420),
              child: Theme(
                data: Theme.of(context).copyWith(
                  colorScheme: isDark
                      ? const ColorScheme.dark(
                          primary: AppColors.careenaTeal,
                          onPrimary: AppColors.white,
                          surface: AppColors.appointmentCalendarSurfaceDark,
                          onSurface: AppColors.white,
                        )
                      : const ColorScheme.light(
                          primary: AppColors.careenaTeal,
                          onPrimary: AppColors.white,
                          onSurface: AppColors.black,
                        ),
                  datePickerTheme: DatePickerThemeData(
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(24),
                    ),
                    headerHeadlineStyle: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 30,
                    ),
                    headerHelpStyle: const TextStyle(fontSize: 20),
                  ),
                ),
                child: child!,
              ),
            ),
          ),
        );
      },
    );

    if (pickedDate != null) {
      setState(() {
        selectedDate = pickedDate;
        dateController.text =
            '${pickedDate.day}.${pickedDate.month}.${pickedDate.year}';
      });
      _announce('Datum ${dateController.text} ausgewählt');
    }
  }

  Future<void> _pickTime() async {
    final pickedTime = await showTimePicker(
      context: context,
      initialTime: TimeOfDay.now(),
      builder: (context, child) {
        final isDark = Theme.of(context).brightness == Brightness.dark;

        return MediaQuery(
          data: MediaQuery.of(context).copyWith(alwaysUse24HourFormat: true),
          child: Theme(
            data: Theme.of(context).copyWith(
              colorScheme: isDark
                  ? const ColorScheme.dark(
                      primary: AppColors.careenaTeal,
                      onPrimary: AppColors.white,
                      surface: AppColors.appointmentCalendarSurfaceDark,
                      onSurface: AppColors.white,
                    )
                  : const ColorScheme.light(
                      primary: AppColors.careenaTeal,
                      onPrimary: AppColors.white,
                      onSurface: AppColors.black,
                    ),
              timePickerTheme: const TimePickerThemeData(
                helpTextStyle: TextStyle(fontSize: 20),
              ),
            ),
            child: child!,
          ),
        );
      },
    );

    if (pickedTime != null) {
      setState(() {
        selectedTime = pickedTime;
        timeController.text =
            '${pickedTime.hour.toString().padLeft(2, '0')}:'
            '${pickedTime.minute.toString().padLeft(2, '0')}';
      });
      _announce('Uhrzeit ${timeController.text} Uhr ausgewählt');
    }
  }

  @override
  void dispose() {
    _observedAuthSession?.removeListener(_handleAuthSessionChanged);
    doctorController.dispose();
    noteController.dispose();
    dateController.dispose();
    timeController.dispose();
    controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: CareenaPageHeader(
        title: 'Terminplanung',
        onBack: () => navigateToHomeFallback(
          context,
          themeController: widget.themeController,
        ),
      ),
      body: ResponsivePageBody(
        maxWidth: 1000,
        padding: const EdgeInsets.all(16),
        scrollable: false,
        child: LayoutBuilder(
          builder: (context, constraints) {
            final authSession = _currentAuthSession();
            final compactHeight = constraints.maxHeight < 360;
            final tightHeight = constraints.maxHeight < 300;
            final smallGap = tightHeight ? 4.0 : (compactHeight ? 8.0 : 16.0);
            final sectionGap = tightHeight
                ? 6.0
                : (compactHeight ? 12.0 : 24.0);
            final titleGap = tightHeight ? 4.0 : (compactHeight ? 6.0 : 12.0);

            final activeProfile = authSession?.activeProfile;
            final canViewAllProfiles =
                activeProfile?.profileType == 'self' ||
                activeProfile?.role == 'owner';

            final headerChildren = <Widget>[
              const AppointmentInfoCard(),
              SizedBox(height: smallGap),
              const Appointment116117Card(),
              SizedBox(height: sectionGap),
              Align(
                alignment: Alignment.centerLeft,
                child: Text(
                  'Deine Termine',
                  style: TextStyle(
                    color: Theme.of(context).colorScheme.onSurface,
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              SizedBox(height: titleGap),
              if (canViewAllProfiles) ...[
                AppointmentProfileFilter(
                  profiles: authSession?.profiles ?? const [],
                  selectedProfileId: selectedProfileId,
                  showAllProfiles: showAllProfiles,
                  onShowAll: _showAllProfilesInAppointments,
                  onProfileSelected: _showProfileInAppointments,
                ),
                if ((authSession?.profiles.length ?? 0) > 1)
                  SizedBox(height: titleGap),
              ],
              AppointmentFilterBar(
                selectedFilter: selectedFilter,
                onFilterChanged: (filter) {
                  setState(() {
                    selectedFilter = filter;
                  });
                },
              ),
              SizedBox(height: smallGap),
            ];

            if (tightHeight) {
              return ListView(
                padding: EdgeInsets.zero,
                children: [
                  ...headerChildren,
                  _buildAppointmentList(shrinkWrap: true),
                ],
              );
            }

            return Column(
              children: [
                ...headerChildren,
                Expanded(child: _buildAppointmentList()),
              ],
            );
          },
        ),
      ),
      floatingActionButtonLocation: FloatingActionButtonLocation.endFloat,
      floatingActionButton: Builder(
        builder: (context) {
          final screenWidth = MediaQuery.of(context).size.width;
          final contentSideInset = screenWidth > 1000
              ? (screenWidth - 1000) / 2
              : 0.0;

          return Padding(
            padding: EdgeInsets.only(right: contentSideInset),
            child: Semantics(
              button: true,
              label: 'Neuen Termin hinzufügen',
              hint: 'Öffnet das Formular für einen Arzt- oder Praxistermin.',
              onTap: _showAddAppointmentDialog,
              child: ExcludeSemantics(
                child: FloatingActionButton(
                  tooltip: 'Neuen Termin hinzufügen',
                  backgroundColor: AppColors.careenaTeal,
                  foregroundColor: AppColors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                  onPressed: _showAddAppointmentDialog,
                  child: const Icon(Icons.add),
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildAppointmentList({bool shrinkWrap = false}) {
    return AppointmentList(
      appointmentsListenable: controller.appointments,
      selectedFilter: selectedFilter,
      selectedProfileId: selectedProfileId,
      showAllProfiles: showAllProfiles,
      shrinkWrap: shrinkWrap,
      onDelete: _showDeleteDialog,
      onEdit: _showEditDialog,
    );
  }

  void _showAllProfilesInAppointments() {
    setState(() {
      showAllProfiles = true;
    });
    _loadRecommendedAppointmentsForCurrentView();
  }

  void _showProfileInAppointments(int profileId) {
    final authSession = _currentAuthSession();
    final profileIsAvailable =
        authSession?.profiles.any((profile) => profile.id == profileId) ??
        false;

    if (authSession != null &&
        profileIsAvailable &&
        authSession.activeProfileId != profileId) {
      setState(() {
        selectedProfileId = profileId;
        showAllProfiles = false;
      });
      authSession.setActiveProfileById(profileId);
      return;
    }

    setState(() {
      selectedProfileId = profileId;
      showAllProfiles = false;
    });
    _loadRecommendedAppointmentsForProfile(profileId);
  }

  void _showAddAppointmentDialog() {
    _clearAppointmentForm();
    String? doctorErrorText;
    String? dateErrorText;

    showDialog(
      context: context,
      builder: (context) {
        return StatefulBuilder(
          builder: (context, setDialogState) {
            return AppointmentDialog(
              title: 'Termin hinzufügen',
              doctorController: doctorController,
              dateController: dateController,
              timeController: timeController,
              noteController: noteController,
              onPickDate: () async {
                await _pickDate();
                if (dateErrorText == null) return;

                setDialogState(() {
                  dateErrorText = null;
                });
              },
              onPickTime: _pickTime,
              onCancel: () {
                _clearAppointmentForm();
                Navigator.pop(context);
              },
              doctorErrorText: doctorErrorText,
              dateErrorText: dateErrorText,
              onDoctorChanged: (_) {
                if (doctorErrorText == null) return;

                setDialogState(() {
                  doctorErrorText = null;
                });
              },
              onSave: () {
                if (doctorController.text.trim().isEmpty) {
                  setDialogState(() {
                    doctorErrorText =
                        'Bitte gib einen Arzt oder eine Praxis ein.';
                  });
                  _announce('Bitte gib einen Arzt oder eine Praxis ein.');
                  return;
                }

                if (_requiresDateForSelectedTime()) {
                  setDialogState(() {
                    dateErrorText = 'Bitte wähle ein Datum aus.';
                  });
                  _announce('Bitte wähle ein Datum aus.');
                  return;
                }

                controller.addAppointment(
                  Appointment(
                    id: DateTime.now().millisecondsSinceEpoch.toString(),
                    profileId: selectedProfileId,
                    doctorName: doctorController.text.trim(),
                    appointmentDate: _buildAppointmentDate(null),
                    note: noteController.text.trim(),
                  ),
                );

                _clearAppointmentForm();
                Navigator.pop(context);
                _showSuccessMessage('Termin gespeichert');
                _announce('Termin gespeichert');
                setState(() {});
              },
            );
          },
        );
      },
    );
  }

  void _showDeleteDialog(Appointment appointment) {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('Termin löschen'),
          content: Text(
            'Möchtest du den Termin bei "${appointment.doctorName}" wirklich löschen?',
          ),
          actions: [
            TextButton(
              style: TextButton.styleFrom(
                foregroundColor: AppColors.careenaTeal,
              ),
              onPressed: () {
                Navigator.pop(context);
              },
              child: const Text('Abbrechen'),
            ),
            FilledButton(
              style: FilledButton.styleFrom(backgroundColor: AppColors.red),
              onPressed: () async {
                final backendId = appointment.backendId;
                final profileId = appointment.profileId;
                if (backendId != null && profileId != null) {
                  try {
                    await AppDependenciesScope.of(
                      this.context,
                    ).appointmentApiService.cancelRecommendedAppointment(
                      profileId: profileId,
                      appointmentId: backendId,
                    );
                  } catch (_) {
                    if (!context.mounted) return;
                    Navigator.pop(context);
                    _showSuccessMessage('Termin konnte nicht storniert werden');
                    return;
                  }
                }
                controller.removeAppointment(appointment.id);
                if (!context.mounted) return;
                Navigator.pop(context);
                final message = backendId == null
                    ? 'Termin gelöscht'
                    : 'Termin storniert';
                _showSuccessMessage(message);
                _announce(message);
              },
              child: const Text('Löschen'),
            ),
          ],
        );
      },
    );
  }

  void _showEditDialog(Appointment appointment) {
    if (appointment.isRecommendation &&
        appointment.backendId != null &&
        appointment.profileId != null &&
        appointment.sessionId != null) {
      _showFhirRescheduleDialog(appointment);
      return;
    }

    final appointmentDate = appointment.appointmentDate;
    final isPendingRecommendation =
        appointment.isRecommendation && appointmentDate == null;

    doctorController.text = isPendingRecommendation
        ? ''
        : appointment.doctorName;
    noteController.text = isPendingRecommendation ? '' : appointment.note;
    selectedDate = appointmentDate;
    selectedTime = appointmentDate == null
        ? null
        : TimeOfDay(hour: appointmentDate.hour, minute: appointmentDate.minute);

    dateController.text = appointmentDate == null
        ? ''
        : '${appointmentDate.day}.'
              '${appointmentDate.month}.'
              '${appointmentDate.year}';

    timeController.text = appointmentDate == null
        ? ''
        : '${appointmentDate.hour.toString().padLeft(2, '0')}:'
              '${appointmentDate.minute.toString().padLeft(2, '0')}';

    String? doctorErrorText;
    String? dateErrorText;

    showDialog(
      context: context,
      builder: (context) {
        return StatefulBuilder(
          builder: (context, setDialogState) {
            return AppointmentDialog(
              title: 'Termin bearbeiten',
              doctorController: doctorController,
              dateController: dateController,
              timeController: timeController,
              noteController: noteController,
              onPickDate: () async {
                await _pickDate();
                if (dateErrorText == null) return;

                setDialogState(() {
                  dateErrorText = null;
                });
              },
              onPickTime: _pickTime,
              onCancel: () {
                _clearAppointmentForm();
                Navigator.pop(context);
              },
              doctorErrorText: doctorErrorText,
              dateErrorText: dateErrorText,
              onDoctorChanged: (_) {
                if (doctorErrorText == null) return;

                setDialogState(() {
                  doctorErrorText = null;
                });
              },
              onSave: () {
                if (doctorController.text.trim().isEmpty) {
                  setDialogState(() {
                    doctorErrorText =
                        'Bitte gib einen Arzt oder eine Praxis ein.';
                  });
                  _announce('Bitte gib einen Arzt oder eine Praxis ein.');
                  return;
                }

                if (_requiresDateForSelectedTime()) {
                  setDialogState(() {
                    dateErrorText = 'Bitte wähle ein Datum aus.';
                  });
                  _announce('Bitte wähle ein Datum aus.');
                  return;
                }

                final updatedAppointmentDate = _buildAppointmentDate(
                  appointmentDate,
                );

                controller.updateAppointment(
                  Appointment(
                    id: appointment.id,
                    backendId: appointment.backendId,
                    profileId: appointment.profileId,
                    sessionId: appointment.sessionId,
                    doctorName: doctorController.text.trim(),
                    appointmentDate: updatedAppointmentDate,
                    note: noteController.text.trim(),
                    isRecommendation:
                        appointment.isRecommendation &&
                        updatedAppointmentDate == null,
                    isCompleted: appointment.isCompleted,
                  ),
                );
                _clearAppointmentForm();
                Navigator.pop(context);
                _showSuccessMessage('Termin aktualisiert');
                _announce('Termin aktualisiert');
              },
            );
          },
        );
      },
    );
  }

  Future<void> _showFhirRescheduleDialog(Appointment appointment) async {
    final postalCodeController = TextEditingController();
    final postalCode = await showDialog<String>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Termin umbuchen'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Gib die PLZ für die erneute 116117-Terminsuche ein.'),
            const SizedBox(height: 8),
            const Text(
              'ⓘ Simulierter 116117-Terminservice – keine echten Arzttermine',
              style: TextStyle(fontSize: 11, color: AppColors.careenaTeal),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: postalCodeController,
              keyboardType: TextInputType.number,
              maxLength: 5,
              decoration: const InputDecoration(
                labelText: 'PLZ',
                counterText: '',
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(dialogContext),
            child: const Text('Abbrechen'),
          ),
          FilledButton(
            onPressed: () {
              final value = postalCodeController.text.trim();
              if (RegExp(r'^\d{5}$').hasMatch(value)) {
                Navigator.pop(dialogContext, value);
              }
            },
            child: const Text('Termine suchen'),
          ),
        ],
      ),
    );
    postalCodeController.dispose();
    if (postalCode == null || !mounted) return;

    final searchService = AppointmentSearchApiService(
      AppDependenciesScope.of(context).apiClient,
    );
    try {
      final response = await searchService.search(
        sessionId: appointment.sessionId!,
        profileId: appointment.profileId!,
        postalCode: postalCode,
      );
      if (!mounted) return;
      final replacement = await showDialog<FhirAppointmentResult>(
        context: context,
        builder: (dialogContext) => SimpleDialog(
          title: const Text('Neuen Termin auswählen'),
          children: [
            for (final candidate in response.appointments)
              SimpleDialogOption(
                onPressed: () => Navigator.pop(dialogContext, candidate),
                child: Padding(
                  padding: const EdgeInsets.symmetric(vertical: 8),
                  child: Text(
                    '${candidate.providerName}\n${candidate.specialty} · '
                    '${candidate.date}, ${candidate.time} Uhr',
                  ),
                ),
              ),
          ],
        ),
      );
      if (replacement == null || !mounted) return;

      final updated = await AppDependenciesScope.of(context)
          .appointmentApiService
          .rescheduleRecommendedAppointment(
            profileId: appointment.profileId!,
            appointmentId: appointment.backendId!,
            sessionId: appointment.sessionId!,
            replacementFhirAppointmentId: replacement.id,
            note: appointment.note,
          );
      controller.updateAppointment(updated);
      if (!mounted) return;
      _showSuccessMessage('Termin wurde erfolgreich umgebucht');
      _announce('Termin wurde umgebucht');
    } catch (_) {
      if (!mounted) return;
      _showSuccessMessage('Termin konnte nicht umgebucht werden');
    }
  }

  DateTime? _buildAppointmentDate(DateTime? fallbackDate) {
    if (selectedDate == null && selectedTime == null) {
      return fallbackDate;
    }

    final date = selectedDate ?? fallbackDate ?? DateTime.now();
    final time =
        selectedTime ??
        (fallbackDate == null
            ? const TimeOfDay(hour: 0, minute: 0)
            : TimeOfDay(hour: fallbackDate.hour, minute: fallbackDate.minute));

    return DateTime(date.year, date.month, date.day, time.hour, time.minute);
  }

  bool _requiresDateForSelectedTime() {
    return selectedDate == null &&
        dateController.text.trim().isEmpty &&
        selectedTime != null;
  }

  void _showSuccessMessage(String message) {
    showCareenaSnackBar(context, message);
  }

  void _announce(String message) {
    SemanticsService.sendAnnouncement(
      View.of(context),
      message,
      Directionality.of(context),
    );
  }

  void _clearAppointmentForm() {
    doctorController.clear();
    noteController.clear();
    dateController.clear();
    timeController.clear();
    selectedDate = null;
    selectedTime = null;
  }
}
