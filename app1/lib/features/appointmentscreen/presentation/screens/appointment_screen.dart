import 'package:app1/core/themes/app_colors.dart';
import 'package:app1/core/widgets/responsive_frame.dart';
import 'package:flutter/material.dart';

import '../../../../core/widgets/careena_page_header.dart';
import '../../controllers/appointment_controller.dart';
import '../../data/models/appointment.dart';
import '../widgets/appointment_116117_card.dart';
import '../widgets/appointment_dialog.dart';
import '../widgets/appointment_empty_state.dart';
import '../widgets/appointment_filter_bar.dart';
import '../widgets/appointment_info_card.dart';
import '../widgets/appointment_tile.dart';
import '../widgets/appointment_profile_filter.dart';
import '../../../authscreen/state/auth_session.dart';

class AppointmentScreen extends StatefulWidget {
  final AuthSession? authSession;
  const AppointmentScreen({super.key, this.authSession});

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
                          onPrimary: Colors.white,
                          surface: Color(0xFF1B2B3D),
                          onSurface: Colors.white,
                        )
                      : const ColorScheme.light(
                          primary: AppColors.careenaTeal,
                          onPrimary: Colors.white,
                          onSurface: Colors.black,
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
    }
  }

  Future<void> _pickTime() async {
    final pickedTime = await showTimePicker(
      context: context,
      initialTime: TimeOfDay.now(),
      builder: (context, child) {
        final isDark = Theme.of(context).brightness == Brightness.dark;

        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: isDark
                ? const ColorScheme.dark(
                    primary: AppColors.careenaTeal,
                    onPrimary: Colors.white,
                    surface: Color(0xFF1B2B3D),
                    onSurface: Colors.white,
                  )
                : const ColorScheme.light(
                    primary: AppColors.careenaTeal,
                    onPrimary: Colors.white,
                    onSurface: Colors.black,
                  ),
            timePickerTheme: const TimePickerThemeData(
              helpTextStyle: TextStyle(fontSize: 20),
            ),
          ),
          child: child!,
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
    }
  }

  @override
  void dispose() {
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
      appBar: const CareenaPageHeader(title: 'Terminplanung'),
      body: ResponsivePageBody(
        maxWidth: 1000,
        padding: const EdgeInsets.all(16),
        scrollable: false,
        child: LayoutBuilder(
          builder: (context, constraints) {
            final compactHeight = constraints.maxHeight < 360;
            final tightHeight = constraints.maxHeight < 300;
            final smallGap = tightHeight ? 4.0 : (compactHeight ? 8.0 : 16.0);
            final sectionGap = tightHeight
                ? 6.0
                : (compactHeight ? 12.0 : 24.0);
            final titleGap = tightHeight ? 4.0 : (compactHeight ? 6.0 : 12.0);

            final activeProfile = widget.authSession?.activeProfile;
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
                  profiles: widget.authSession?.profiles ?? const [],
                  selectedProfileId: selectedProfileId,
                  showAllProfiles: showAllProfiles,
                  onShowAll: () {
                    setState(() {
                      showAllProfiles = true;
                    });
                  },
                  onProfileSelected: (profileId) {
                    setState(() {
                      selectedProfileId = profileId;
                      showAllProfiles = false;
                    });
                  },
                ),
                if ((widget.authSession?.profiles.length ?? 0) > 1)
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
                  _buildAppointmentContent(shrinkWrap: true),
                ],
              );
            }

            return Column(
              children: [
                ...headerChildren,
                Expanded(child: _buildAppointmentContent()),
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
            child: FloatingActionButton(
              backgroundColor: AppColors.careenaTeal,
              foregroundColor: Colors.white,
              onPressed: _showAddAppointmentDialog,
              child: const Icon(Icons.add),
            ),
          );
        },
      ),
    );
  }

  Widget _buildAppointmentContent({bool shrinkWrap = false}) {
    return ValueListenableBuilder(
      valueListenable: controller.appointments,
      builder: (context, appointments, child) {
        List<Appointment> filteredAppointments = List.from(appointments);

        if (!showAllProfiles) {
          filteredAppointments = filteredAppointments.where((appointment) {
            return appointment.profileId == selectedProfileId;
          }).toList();
        }

        if (selectedFilter == 'Kommend') {
          filteredAppointments = filteredAppointments.where((appointment) {
            final appointmentDate = appointment.appointmentDate;
            return appointmentDate != null &&
                appointmentDate.isAfter(DateTime.now());
          }).toList();
        }

        if (selectedFilter == 'Vergangen') {
          filteredAppointments = filteredAppointments.where((appointment) {
            final appointmentDate = appointment.appointmentDate;
            return appointmentDate != null &&
                appointmentDate.isBefore(DateTime.now());
          }).toList();
        }

        if (selectedFilter == 'Erledigt') {
          filteredAppointments = filteredAppointments.where((appointment) {
            return appointment.isCompleted;
          }).toList();
        }

        if (filteredAppointments.isEmpty && selectedFilter == 'Alle') {
          if (shrinkWrap) {
            return const SizedBox(height: 180, child: AppointmentEmptyState());
          }

          return const AppointmentEmptyState();
        }

        final recommendedAppointments = selectedFilter == 'Alle'
            ? filteredAppointments.where((appointment) {
                return appointment.isRecommendation &&
                    appointment.appointmentDate == null;
              }).toList()
            : <Appointment>[];

        filteredAppointments = filteredAppointments.where((appointment) {
          return !(appointment.isRecommendation &&
              appointment.appointmentDate == null);
        }).toList();

        filteredAppointments.sort((a, b) {
          final firstDate = a.appointmentDate;
          final secondDate = b.appointmentDate;

          if (firstDate == null && secondDate == null) return 0;
          if (firstDate == null) return -1;
          if (secondDate == null) return 1;

          return firstDate.compareTo(secondDate);
        });

        if (recommendedAppointments.isEmpty && filteredAppointments.isEmpty) {
          const emptyFilter = Center(
            child: Text('Keine Termine in diesem Filter.'),
          );

          if (shrinkWrap) {
            return const Padding(
              padding: EdgeInsets.symmetric(vertical: 24),
              child: emptyFilter,
            );
          }

          return emptyFilter;
        }

        return ListView(
          shrinkWrap: shrinkWrap,
          physics: shrinkWrap ? const NeverScrollableScrollPhysics() : null,
          children: [
            if (recommendedAppointments.isNotEmpty) ...[
              _AppointmentSectionHeader(
                icon: Icons.auto_awesome_outlined,
                title: 'Empfohlene nächste Schritte',
                subtitle:
                    'Von Careena vorgeschlagene Termine, die du noch eintragen kannst.',
              ),
              const SizedBox(height: 8),
              for (final appointment in recommendedAppointments)
                AppointmentTile(
                  appointment: appointment,
                  onToggleCompleted: () {
                    controller.toggleAppointment(appointment.id);
                  },
                  onDelete: () {
                    _showDeleteDialog(appointment);
                  },
                  onEdit: () {
                    _showEditDialog(appointment);
                  },
                ),
              if (filteredAppointments.isNotEmpty) const SizedBox(height: 12),
            ],
            if (filteredAppointments.isNotEmpty) ...[
              if (recommendedAppointments.isNotEmpty) ...[
                const _AppointmentSectionHeader(
                  icon: Icons.event_available_outlined,
                  title: 'Geplante Termine',
                ),
                const SizedBox(height: 8),
              ],
              for (final appointment in filteredAppointments)
                AppointmentTile(
                  appointment: appointment,
                  onToggleCompleted: () {
                    controller.toggleAppointment(appointment.id);
                  },
                  onDelete: () {
                    _showDeleteDialog(appointment);
                  },
                  onEdit: () {
                    _showEditDialog(appointment);
                  },
                ),
            ],
          ],
        );
      },
    );
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
                  return;
                }

                if (_requiresDateForSelectedTime()) {
                  setDialogState(() {
                    dateErrorText = 'Bitte wähle ein Datum aus.';
                  });
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
              style: FilledButton.styleFrom(backgroundColor: Colors.red),
              onPressed: () {
                controller.removeAppointment(appointment.id);
                _showSuccessMessage('Termin gelöscht');
                Navigator.pop(context);
              },
              child: const Text('Löschen'),
            ),
          ],
        );
      },
    );
  }

  void _showEditDialog(Appointment appointment) {
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
                  return;
                }

                if (_requiresDateForSelectedTime()) {
                  setDialogState(() {
                    dateErrorText = 'Bitte wähle ein Datum aus.';
                  });
                  return;
                }

                final updatedAppointmentDate = _buildAppointmentDate(
                  appointmentDate,
                );

                controller.updateAppointment(
                  Appointment(
                    id: appointment.id,
                    profileId: appointment.profileId,
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
                _showSuccessMessage('Termin aktualisiert');
                Navigator.pop(context);
              },
            );
          },
        );
      },
    );
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
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        backgroundColor: AppColors.careenaTeal,
        content: Text(
          message,
          style: const TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
            fontSize: 16,
          ),
        ),
      ),
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

class _AppointmentSectionHeader extends StatelessWidget {
  final IconData icon;
  final String title;
  final String? subtitle;

  const _AppointmentSectionHeader({
    required this.icon,
    required this.title,
    this.subtitle,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Padding(
      padding: const EdgeInsets.only(top: 4, bottom: 2),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 20, color: AppColors.careenaTeal),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: TextStyle(
                    color: colorScheme.onSurface,
                    fontSize: 15,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                if (subtitle != null) ...[
                  const SizedBox(height: 2),
                  Text(
                    subtitle!,
                    style: TextStyle(
                      color: colorScheme.onSurfaceVariant,
                      fontSize: 13,
                    ),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }
}
