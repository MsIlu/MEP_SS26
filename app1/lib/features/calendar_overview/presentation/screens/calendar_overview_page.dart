import 'package:app1/app/app_dependencies_scope.dart';
import 'package:app1/core/network/api_client.dart';
import 'package:app1/core/themes/app_colors.dart';
import 'package:app1/core/themes/theme_controller.dart';
import 'package:app1/core/widgets/careena_page_header.dart';
import 'package:app1/core/widgets/responsive_frame.dart';
import 'package:app1/features/appointmentscreen/controllers/appointment_controller.dart';
import 'package:app1/features/appointmentscreen/data/models/appointment.dart';
import 'package:app1/features/appointmentscreen/presentation/screens/appointment_screen.dart';
import 'package:app1/features/authscreen/state/auth_session.dart';
import 'package:app1/features/chatscreen/presentation/screens/chat_history_screen.dart';
import 'package:app1/features/homescreen/presentation/screens/home_screen.dart';
import 'package:app1/features/homescreen/presentation/widgets/custom_bottom_nav.dart';
import 'package:app1/features/medication_plan/data/medication_api_service.dart';
import 'package:app1/features/medication_plan/data/medication_entry.dart';
import 'package:app1/features/medication_plan/data/medication_repository.dart';
import 'package:app1/features/medication_plan/presentation/models/planned_medication_dose.dart';
import 'package:app1/features/medication_plan/presentation/screens/medication_plan_page.dart';
import 'package:app1/features/medication_plan/presentation/utils/medication_plan_builder.dart';
import 'package:app1/features/settings/presentation/screens/settings_page.dart';
import 'package:app1/features/symptom_diary/data/symptom_entry.dart';
import 'package:app1/features/symptom_diary/data/symptom_repository.dart';
import 'package:app1/features/symptom_diary/presentation/screens/symptom_diary_page.dart';
import 'package:flutter/material.dart';

/// Calendar overview combining appointments, symptoms, and medication plans.
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
  late DateTime _focusedMonth;
  late DateTime _selectedDate;
  List<SymptomEntry> _symptoms = const [];
  List<MedicationEntry> _medications = const [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    final now = DateTime.now();
    _focusedMonth = DateTime(now.year, now.month);
    _selectedDate = DateTime(now.year, now.month, now.day);
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
                  _MonthHeader(
                    month: _focusedMonth,
                    onPrevious: () => _shiftMonth(-1),
                    onNext: () => _shiftMonth(1),
                  ),
                  const SizedBox(height: 12),
                  _CalendarGrid(
                    focusedMonth: _focusedMonth,
                    selectedDate: _selectedDate,
                    hasItems: _hasItemsForDate,
                    onSelected: _selectDate,
                  ),
                  const SizedBox(height: 18),
                  if (_isLoading)
                    const Center(child: CircularProgressIndicator())
                  else
                    _DayOverview(
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
      return appointmentDate != null && _isSameDay(appointmentDate, date);
    }).toList();
  }

  List<SymptomEntry> _symptomsForDate(DateTime date) {
    return _symptoms.where((entry) => _isSameDay(entry.date, date)).toList();
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
      // In isolated widget tests the home route is already below the calendar.
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

class _MonthHeader extends StatelessWidget {
  final DateTime month;
  final VoidCallback onPrevious;
  final VoidCallback onNext;

  const _MonthHeader({
    required this.month,
    required this.onPrevious,
    required this.onNext,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        IconButton(
          tooltip: 'Vorheriger Monat',
          onPressed: onPrevious,
          icon: const Icon(Icons.chevron_left),
        ),
        Expanded(
          child: Text(
            _monthLabel(month),
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
              fontWeight: FontWeight.w800,
            ),
          ),
        ),
        IconButton(
          tooltip: 'Nächster Monat',
          onPressed: onNext,
          icon: const Icon(Icons.chevron_right),
        ),
      ],
    );
  }
}

class _CalendarGrid extends StatelessWidget {
  final DateTime focusedMonth;
  final DateTime selectedDate;
  final bool Function(DateTime date) hasItems;
  final ValueChanged<DateTime> onSelected;

  const _CalendarGrid({
    required this.focusedMonth,
    required this.selectedDate,
    required this.hasItems,
    required this.onSelected,
  });

  @override
  Widget build(BuildContext context) {
    final days = _visibleMonthDays(focusedMonth);

    return Column(
      children: [
        Row(
          children: [
            for (final label in ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So'])
              Expanded(child: Center(child: Text(label))),
          ],
        ),
        const SizedBox(height: 8),
        GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: days.length,
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 7,
            childAspectRatio: 1.35,
            mainAxisSpacing: 4,
            crossAxisSpacing: 4,
          ),
          itemBuilder: (context, index) {
            final date = days[index];
            if (date == null) return const SizedBox.shrink();

            final isSelected = _isSameDay(date, selectedDate);
            final hasMarker = hasItems(date);

            return _CalendarDayTile(
              date: date,
              isSelected: isSelected,
              hasMarker: hasMarker,
              onTap: () => onSelected(date),
            );
          },
        ),
      ],
    );
  }
}

class _CalendarDayTile extends StatelessWidget {
  final DateTime date;
  final bool isSelected;
  final bool hasMarker;
  final VoidCallback onTap;

  const _CalendarDayTile({
    required this.date,
    required this.isSelected,
    required this.hasMarker,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final backgroundColor = isSelected
        ? AppColors.careenaTeal
        : Theme.of(context).brightness == Brightness.dark
        ? AppColors.darkElevatedSurface
        : AppColors.careenaNoteBackground;
    final textColor = isSelected
        ? AppColors.white
        : colorScheme.onSurface;

    return InkWell(
      borderRadius: BorderRadius.circular(8),
      onTap: onTap,
      child: DecoratedBox(
        decoration: BoxDecoration(
          color: backgroundColor,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: isSelected
                ? AppColors.careenaTeal
                : AppColors.careenaBorder,
          ),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              '${date.day}',
              style: TextStyle(color: textColor, fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 4),
            SizedBox.square(
              dimension: 5,
              child: DecoratedBox(
                decoration: BoxDecoration(
                  color: hasMarker
                      ? (isSelected ? AppColors.white : AppColors.careenaTeal)
                      : AppColors.transparent,
                  shape: BoxShape.circle,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _DayOverview extends StatelessWidget {
  final DateTime date;
  final List<Appointment> appointments;
  final List<SymptomEntry> symptoms;
  final List<PlannedMedicationDose> medications;
  final ValueChanged<Appointment> onAppointmentTap;
  final ValueChanged<SymptomEntry> onSymptomTap;
  final ValueChanged<MedicationEntry> onMedicationTap;

  const _DayOverview({
    required this.date,
    required this.appointments,
    required this.symptoms,
    required this.medications,
    required this.onAppointmentTap,
    required this.onSymptomTap,
    required this.onMedicationTap,
  });

  @override
  Widget build(BuildContext context) {
    final hasAnyItems =
        appointments.isNotEmpty || symptoms.isNotEmpty || medications.isNotEmpty;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          _dateLabel(date),
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.w800,
          ),
        ),
        const SizedBox(height: 12),
        if (!hasAnyItems)
          const _CalendarInfoCard(
            icon: Icons.event_available_outlined,
            title: 'Keine Einträge',
            lines: [
              _CalendarInfoLine(
                text: 'Für diesen Tag sind keine Einträge vorhanden.',
                onTap: _noop,
              ),
            ],
          )
        else ...[
          _CalendarInfoCard(
            icon: Icons.event_outlined,
            title: 'Termine',
            lines: appointments
                .map((appointment) {
                  final time = appointment.appointmentDate == null
                      ? ''
                      : '${_twoDigits(appointment.appointmentDate!.hour)}:'
                            '${_twoDigits(appointment.appointmentDate!.minute)} ';
                  return _CalendarInfoLine(
                    text: '$time${appointment.doctorName}',
                    onTap: () => onAppointmentTap(appointment),
                  );
                })
                .toList(),
          ),
          _CalendarInfoCard(
            icon: Icons.menu_book_outlined,
            title: 'Symptome',
            lines: symptoms
                .map(
                  (entry) => _CalendarInfoLine(
                    text: _symptomLine(entry),
                    onTap: () => onSymptomTap(entry),
                  ),
                )
                .toList(),
          ),
          _CalendarInfoCard(
            icon: Icons.medication_outlined,
            title: 'Medikamente',
            lines: medications
                .map((dose) {
                  final time = dose.intakeTime;
                  final suffix = dose.entry.intakeTimes.length > 1
                      ? ' (${dose.doseIndex + 1}. Einnahme)'
                      : '';
                  return _CalendarInfoLine(
                    text:
                        '${_twoDigits(time.hour)}:${_twoDigits(time.minute)} '
                        '${dose.entry.name} ${dose.entry.dose}$suffix',
                    onTap: () => onMedicationTap(dose.entry),
                  );
                })
                .toList(),
          ),
        ],
      ],
    );
  }
}

class _CalendarInfoCard extends StatefulWidget {
  final IconData icon;
  final String title;
  final List<_CalendarInfoLine> lines;

  const _CalendarInfoCard({
    required this.icon,
    required this.title,
    required this.lines,
  });

  @override
  State<_CalendarInfoCard> createState() => _CalendarInfoCardState();
}

class _CalendarInfoCardState extends State<_CalendarInfoCard> {
  bool _isExpanded = true;

  @override
  Widget build(BuildContext context) {
    if (widget.lines.isEmpty) return const SizedBox.shrink();

    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: DecoratedBox(
        decoration: BoxDecoration(
          color: Theme.of(context).colorScheme.surface,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: AppColors.careenaBorder),
        ),
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(widget.icon, color: AppColors.careenaTeal),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    InkWell(
                      onTap: () => setState(() => _isExpanded = !_isExpanded),
                      child: Row(
                        children: [
                          Expanded(
                            child: Text(
                              widget.title,
                              style: const TextStyle(fontWeight: FontWeight.w800),
                            ),
                          ),
                          Icon(
                            _isExpanded
                                ? Icons.keyboard_arrow_up
                                : Icons.keyboard_arrow_down,
                            color: AppColors.careenaTeal,
                          ),
                        ],
                      ),
                    ),
                    if (_isExpanded) ...[
                      const SizedBox(height: 6),
                      for (final line in widget.lines)
                        _CalendarInfoRow(line: line),
                    ],
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _CalendarInfoLine {
  final String text;
  final VoidCallback onTap;

  const _CalendarInfoLine({required this.text, required this.onTap});
}

class _CalendarInfoRow extends StatelessWidget {
  final _CalendarInfoLine line;

  const _CalendarInfoRow({required this.line});

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: line.onTap,
      child: Padding(
        padding: const EdgeInsets.only(bottom: 3),
        child: Row(
          children: [
            Expanded(child: Text('• ${line.text}')),
            const Icon(Icons.chevron_right, size: 18, color: AppColors.careenaTeal),
          ],
        ),
      ),
    );
  }
}

List<DateTime?> _visibleMonthDays(DateTime month) {
  final firstDay = DateTime(month.year, month.month);
  final leadingDays = firstDay.weekday - DateTime.monday;
  final daysInMonth = DateTime(month.year, month.month + 1, 0).day;
  final currentMonthDays = List<DateTime?>.generate(
    daysInMonth,
    (index) => DateTime(month.year, month.month, index + 1),
  );
  final totalCells = leadingDays + currentMonthDays.length;
  final trailingDays = (7 - totalCells % 7) % 7;

  return [
    ...List<DateTime?>.filled(leadingDays, null),
    ...currentMonthDays,
    ...List<DateTime?>.filled(trailingDays, null),
  ];
}

String _symptomLine(SymptomEntry entry) {
  final bodyArea = entry.bodyArea.trim();
  if (bodyArea.isEmpty) return entry.symptom;
  return '${entry.symptom} ($bodyArea)';
}

bool _isSameDay(DateTime first, DateTime second) {
  return first.year == second.year &&
      first.month == second.month &&
      first.day == second.day;
}

String _monthLabel(DateTime date) {
  return '${_monthName(date.month)} ${date.year}';
}

String _dateLabel(DateTime date) {
  return '${date.day}. ${_monthName(date.month)} ${date.year}';
}

String _monthName(int month) {
  return const [
    'Januar',
    'Februar',
    'März',
    'April',
    'Mai',
    'Juni',
    'Juli',
    'August',
    'September',
    'Oktober',
    'November',
    'Dezember',
  ][month - 1];
}

String _twoDigits(int value) => value.toString().padLeft(2, '0');

void _noop() {}
