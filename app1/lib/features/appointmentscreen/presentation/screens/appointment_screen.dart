import 'package:app1/core/themes/app_colors.dart';
import 'package:app1/core/themes/theme_controller.dart';
import 'package:app1/core/widgets/responsive_frame.dart';
import 'package:flutter/material.dart';

import '../../../../core/widgets/careena_page_header.dart';
import '../../controllers/appointment_controller.dart';
import '../../data/models/appointment.dart';
import '../widgets/appointment_116117_card.dart';
import '../widgets/appointment_dialog.dart';
import '../widgets/appointment_filter_bar.dart';
import '../widgets/appointment_info_card.dart';
import '../widgets/appointment_list.dart';

class AppointmentScreen extends StatefulWidget {
  final ThemeController? themeController;
  final String? initialAppointmentId;

  const AppointmentScreen({
    super.key,
    this.themeController,
    this.initialAppointmentId,
  });

  @override
  State<AppointmentScreen> createState() => _AppointmentScreenState();
}

class _AppointmentScreenState extends State<AppointmentScreen> {
  final AppointmentController controller = AppointmentController();
  final doctorController = TextEditingController();
  final noteController = TextEditingController();
  final dateController = TextEditingController();
  final timeController = TextEditingController();

  DateTime? selectedDate;
  TimeOfDay? selectedTime;

  String selectedFilter = 'Alle';

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _openInitialAppointment();
    });
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
            child: FloatingActionButton(
              backgroundColor: AppColors.careenaTeal,
              foregroundColor: AppColors.white,
              onPressed: _showAddAppointmentDialog,
              child: const Icon(Icons.add),
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
      shrinkWrap: shrinkWrap,
      onToggleCompleted: (appointment) {
        controller.toggleAppointment(appointment.id);
      },
      onDelete: _showDeleteDialog,
      onEdit: _showEditDialog,
    );
  }

  void _showAddAppointmentDialog() {
    _clearAppointmentForm();
    showDialog(
      context: context,
      builder: (context) {
        return AppointmentDialog(
          title: 'Termin hinzufügen',
          doctorController: doctorController,
          dateController: dateController,
          timeController: timeController,
          noteController: noteController,
          onPickDate: _pickDate,
          onPickTime: _pickTime,
          onCancel: () {
            _clearAppointmentForm();
            Navigator.pop(context);
          },
          onSave: () {
            if (doctorController.text.trim().isEmpty) {
              return;
            }

            controller.addAppointment(
              Appointment(
                id: DateTime.now().millisecondsSinceEpoch.toString(),
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

    showDialog(
      context: context,
      builder: (context) {
        return AppointmentDialog(
          title: 'Termin bearbeiten',
          doctorController: doctorController,
          dateController: dateController,
          timeController: timeController,
          noteController: noteController,
          onPickDate: _pickDate,
          onPickTime: _pickTime,
          onCancel: () {
            _clearAppointmentForm();
            Navigator.pop(context);
          },
          onSave: () {
            if (doctorController.text.trim().isEmpty) {
              return;
            }

            final updatedAppointmentDate = _buildAppointmentDate(
              appointmentDate,
            );

            controller.updateAppointment(
              Appointment(
                id: appointment.id,
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

  void _showSuccessMessage(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        backgroundColor: AppColors.careenaTeal,
        content: Text(
          message,
          style: const TextStyle(
            color: AppColors.white,
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
