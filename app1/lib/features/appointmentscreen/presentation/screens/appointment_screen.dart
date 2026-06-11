import 'package:flutter/material.dart';
import 'package:app1/core/themes/app_colors.dart';
import '../widgets/appointment_empty_state.dart';
import '../widgets/appointment_info_card.dart';
import '../widgets/appointment_116117_card.dart';
import '../../controllers/appointment_controller.dart';
import '../../data/models/appointment.dart';
import '../widgets/appointment_tile.dart';
//import '../widgets/add_appointment_dialog.dart';

class AppointmentScreen extends StatefulWidget {
  const AppointmentScreen({super.key});

  @override
  State<AppointmentScreen> createState() => _AppointmentScreenState();
}

class _AppointmentScreenState extends State<AppointmentScreen> {
  final AppointmentController controller = AppointmentController();
  final doctorController = TextEditingController();
  final noteController = TextEditingController();
  final dateController = TextEditingController();
  DateTime? selectedDate;
  final timeController = TextEditingController();
  TimeOfDay? selectedTime;

  Future<void> _pickDate() async {
    final pickedDate = await showDatePicker(
      context: context,
      initialDate: DateTime.now(),
      firstDate: DateTime.now(),
      lastDate: DateTime(2100),
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: const ColorScheme.light(
              primary: AppColors.careenaTeal,
              onPrimary: Colors.white,
              onSurface: Colors.black,
            ),
          ),
          child: child!,
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
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: const ColorScheme.light(
              primary: AppColors.careenaTeal,
              onPrimary: Colors.white,
              onSurface: Colors.black,
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
      appBar: AppBar(
        elevation: 0,
        backgroundColor: Theme.of(context).scaffoldBackgroundColor,

        leading: Padding(
          padding: const EdgeInsets.only(left: 12),
          child: IconButton(
            tooltip: 'Zurück',
            style: IconButton.styleFrom(
              backgroundColor: AppColors.careenaTeal,
              foregroundColor: Colors.white,
              shape: const CircleBorder(),
              fixedSize: const Size(44, 44),
            ),
            onPressed: () => Navigator.pop(context),
            icon: const Icon(Icons.west),
          ),
        ),

        title: Text(
          'Terminplanung',
          style: TextStyle(
            color: Theme.of(context).colorScheme.onSurface,
            fontWeight: FontWeight.bold,
          ),
        ),

        centerTitle: true,
      ),

      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            const AppointmentInfoCard(),
            const SizedBox(height: 16),

            const Appointment116117Card(),
            const SizedBox(height: 24),

            const Align(
              alignment: Alignment.centerLeft,
              child: Text(
                'Deine Termine',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
            ),

            Expanded(
              child: ValueListenableBuilder(
                valueListenable: controller.appointments,
                builder: (context, appointments, child) {
                  if (appointments.isEmpty) {
                    return const AppointmentEmptyState();
                  }

                  final sortedAppointments = [...appointments];

sortedAppointments.sort(
  (a, b) => a.appointmentDate.compareTo(
    b.appointmentDate,
  ),
);

                  return ListView.builder(
                    itemCount: sortedAppointments.length,
                    itemBuilder: (context, index) {
                      final appointment = sortedAppointments[index];

                      return AppointmentTile(
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
                      );
                    },
                  );
                },
              ),
            ),
          ],
        ),
      ),

      floatingActionButton: FloatingActionButton(
        backgroundColor: AppColors.careenaTeal,
        foregroundColor: Colors.white,
        onPressed: _showAddAppointmentDialog,
        child: const Icon(Icons.add),
      ),
    );
  }

  void _showAddAppointmentDialog() {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text(
            'Termin hinzufügen',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),

          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: doctorController,
                decoration: InputDecoration(
                  labelText: 'Arzt',

                  prefixIcon: const Icon(
                    Icons.medical_services,
                    color: AppColors.careenaTeal,
                  ),

                  labelStyle: const TextStyle(color: AppColors.careenaTeal),

                  floatingLabelStyle: const TextStyle(
                    color: AppColors.careenaTeal,
                  ),

                  focusedBorder: OutlineInputBorder(
                    borderSide: const BorderSide(
                      color: AppColors.careenaTeal,
                      width: 2,
                    ),
                    borderRadius: BorderRadius.circular(12),
                  ),

                  enabledBorder: OutlineInputBorder(
                    borderSide: BorderSide(color: Colors.grey.shade300),
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),

              const SizedBox(height: 12),

              TextField(
                controller: dateController,
                readOnly: true,
                onTap: _pickDate,

                decoration: InputDecoration(
                  labelText: 'Datum',

                  prefixIcon: const Icon(
                    Icons.calendar_month,
                    color: AppColors.careenaTeal,
                  ),

                  labelStyle: const TextStyle(color: AppColors.careenaTeal),

                  floatingLabelStyle: const TextStyle(
                    color: AppColors.careenaTeal,
                  ),

                  focusedBorder: OutlineInputBorder(
                    borderSide: const BorderSide(
                      color: AppColors.careenaTeal,
                      width: 2,
                    ),
                    borderRadius: BorderRadius.circular(12),
                  ),

                  enabledBorder: OutlineInputBorder(
                    borderSide: BorderSide(color: Colors.grey.shade300),
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),

              const SizedBox(height: 12),

              TextField(
                controller: timeController,
                readOnly: true,
                onTap: _pickTime,

                decoration: InputDecoration(
                  labelText: 'Uhrzeit',

                  prefixIcon: const Icon(
                    Icons.access_time,
                    color: AppColors.careenaTeal,
                  ),

                  labelStyle: const TextStyle(color: AppColors.careenaTeal),

                  floatingLabelStyle: const TextStyle(
                    color: AppColors.careenaTeal,
                  ),

                  focusedBorder: OutlineInputBorder(
                    borderSide: const BorderSide(
                      color: AppColors.careenaTeal,
                      width: 2,
                    ),
                    borderRadius: BorderRadius.circular(12),
                  ),

                  enabledBorder: OutlineInputBorder(
                    borderSide: BorderSide(color: Colors.grey.shade300),
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),

              const SizedBox(height: 12),

              TextField(
                controller: noteController,
                decoration: InputDecoration(
                  labelText: 'Notiz',

                  prefixIcon: const Icon(
                    Icons.note_alt_outlined,
                    color: AppColors.careenaTeal,
                  ),

                  labelStyle: const TextStyle(color: AppColors.careenaTeal),

                  floatingLabelStyle: const TextStyle(
                    color: AppColors.careenaTeal,
                  ),

                  focusedBorder: OutlineInputBorder(
                    borderSide: const BorderSide(
                      color: AppColors.careenaTeal,
                      width: 2,
                    ),
                    borderRadius: BorderRadius.circular(12),
                  ),

                  enabledBorder: OutlineInputBorder(
                    borderSide: BorderSide(color: Colors.grey.shade300),
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),
            ],
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
              style: FilledButton.styleFrom(
                backgroundColor: AppColors.careenaTeal,
                foregroundColor: Colors.white,
              ),
              onPressed: () {
                if (doctorController.text.trim().isEmpty) {
                  return;
                }

                controller.addAppointment(
                  Appointment(
                    id: DateTime.now().millisecondsSinceEpoch.toString(),
                    doctorName: doctorController.text.trim(),
                    appointmentDate: DateTime(
                      selectedDate?.year ?? DateTime.now().year,
                      selectedDate?.month ?? DateTime.now().month,
                      selectedDate?.day ?? DateTime.now().day,
                      selectedTime?.hour ?? 0,
                      selectedTime?.minute ?? 0,
                    ),
                    note: noteController.text.trim(),
                  ),
                );

                doctorController.clear();
                noteController.clear();
                dateController.clear();
                timeController.clear();
                selectedDate = null;
                selectedTime = null;
                Navigator.pop(context);
                setState(() {});
              },
              child: const Text('Speichern'),
            ),
          ],
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
              onPressed: () {
                Navigator.pop(context);
              },
              child: const Text('Abbrechen'),
            ),

            FilledButton(
              style: FilledButton.styleFrom(backgroundColor: Colors.red),
              onPressed: () {
                controller.removeAppointment(appointment.id);

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
    doctorController.text = appointment.doctorName;
    noteController.text = appointment.note;
    selectedDate = appointment.appointmentDate;
    selectedTime = TimeOfDay(
      hour: appointment.appointmentDate.hour,
      minute: appointment.appointmentDate.minute,
    );

    dateController.text =
        '${appointment.appointmentDate.day}.'
        '${appointment.appointmentDate.month}.'
        '${appointment.appointmentDate.year}';

    timeController.text =
        '${appointment.appointmentDate.hour.toString().padLeft(2, '0')}:'
        '${appointment.appointmentDate.minute.toString().padLeft(2, '0')}';

    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text(
            'Termin bearbeiten',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),

          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: doctorController,
                decoration: InputDecoration(
                  labelText: 'Arzt',
                  prefixIcon: const Icon(
                    Icons.medical_services,
                    color: AppColors.careenaTeal,
                  ),

                  labelStyle: const TextStyle(color: AppColors.careenaTeal),
                  floatingLabelStyle: const TextStyle(
                    color: AppColors.careenaTeal,
                  ),

                  focusedBorder: OutlineInputBorder(
                    borderSide: const BorderSide(
                      color: AppColors.careenaTeal,
                      width: 2,
                    ),
                    borderRadius: BorderRadius.circular(12),
                  ),

                  enabledBorder: OutlineInputBorder(
                    borderSide: BorderSide(color: Colors.grey.shade300),
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),

              const SizedBox(height: 12),

              TextField(
                controller: dateController,
                readOnly: true,
                onTap: _pickDate,
                decoration: InputDecoration(
                  labelText: 'Datum',
                  prefixIcon: const Icon(
                    Icons.calendar_month,
                    color: AppColors.careenaTeal,
                  ),

                  labelStyle: const TextStyle(color: AppColors.careenaTeal),
                  floatingLabelStyle: const TextStyle(
                    color: AppColors.careenaTeal,
                  ),

                  focusedBorder: OutlineInputBorder(
                    borderSide: const BorderSide(
                      color: AppColors.careenaTeal,
                      width: 2,
                    ),
                    borderRadius: BorderRadius.circular(12),
                  ),

                  enabledBorder: OutlineInputBorder(
                    borderSide: BorderSide(color: Colors.grey.shade300),
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),

              const SizedBox(height: 12),

              TextField(
                controller: timeController,
                readOnly: true,
                onTap: _pickTime,

                decoration: InputDecoration(
                  labelText: 'Uhrzeit',

                  prefixIcon: const Icon(
                    Icons.access_time,
                    color: AppColors.careenaTeal,
                  ),

                  labelStyle: const TextStyle(color: AppColors.careenaTeal),

                  floatingLabelStyle: const TextStyle(
                    color: AppColors.careenaTeal,
                  ),

                  focusedBorder: OutlineInputBorder(
                    borderSide: const BorderSide(
                      color: AppColors.careenaTeal,
                      width: 2,
                    ),
                    borderRadius: BorderRadius.circular(12),
                  ),

                  enabledBorder: OutlineInputBorder(
                    borderSide: BorderSide(color: Colors.grey.shade300),
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),

              const SizedBox(height: 12),

              TextField(
                controller: noteController,
                decoration: InputDecoration(
                  labelText: 'Notiz',

                  prefixIcon: const Icon(
                    Icons.note_alt_outlined,
                    color: AppColors.careenaTeal,
                  ),

                  labelStyle: const TextStyle(color: AppColors.careenaTeal),

                  floatingLabelStyle: const TextStyle(
                    color: AppColors.careenaTeal,
                  ),

                  focusedBorder: OutlineInputBorder(
                    borderSide: const BorderSide(
                      color: AppColors.careenaTeal,
                      width: 2,
                    ),
                    borderRadius: BorderRadius.circular(12),
                  ),

                  enabledBorder: OutlineInputBorder(
                    borderSide: BorderSide(color: Colors.grey.shade300),
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),
            ],
          ),

          actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(context);
            },
            child: const Text('Abbrechen'),
          ),

          FilledButton(
            onPressed: () {
              controller.updateAppointment(
                Appointment(
                  id: appointment.id,
                  doctorName: doctorController.text.trim(),
                  appointmentDate: DateTime(
                    selectedDate?.year ??
                        appointment.appointmentDate.year,
                    selectedDate?.month ??
                        appointment.appointmentDate.month,
                    selectedDate?.day ??
                        appointment.appointmentDate.day,
                    selectedTime?.hour ??
                        appointment.appointmentDate.hour,
                    selectedTime?.minute ??
                        appointment.appointmentDate.minute,
                  ),
                  note: noteController.text.trim(),
                  isCompleted: appointment.isCompleted,
                ),
              );
              Navigator.pop(context);
            },
            child: const Text('Speichern'),
          ),
        ],
      );
    },
  );
}
}