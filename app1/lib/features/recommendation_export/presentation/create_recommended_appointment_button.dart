import 'package:app1/core/themes/app_colors.dart';
import 'package:app1/features/appointmentscreen/controllers/appointment_controller.dart';
import 'package:app1/features/appointmentscreen/data/models/appointment.dart';
import 'package:app1/features/appointmentscreen/presentation/screens/appointment_screen.dart';
import 'package:flutter/material.dart';

class CreateRecommendedAppointmentButton extends StatelessWidget {
  final String title;

  const CreateRecommendedAppointmentButton({super.key, required this.title});

  @override
  Widget build(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    final buttonColor = isDarkMode
        ? AppColors.toolbarButtonBackgroundDark
        : AppColors.careenaTeal;
    final textColor = isDarkMode
        ? AppColors.toolbarButtonForegroundDark
        : Colors.white;

    return FilledButton.icon(
      style: FilledButton.styleFrom(
        backgroundColor: buttonColor,
        foregroundColor: textColor,
        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
      ),
      icon: const Icon(Icons.event_available_outlined),
      label: const Text('Termin vereinbaren'),
      onPressed: () => _createAppointment(context),
    );
  }

  Future<void> _createAppointment(BuildContext context) async {
    final wasCreated = AppointmentController()
        .addRecommendedAppointmentIfMissing(
          Appointment(
            id: DateTime.now().millisecondsSinceEpoch.toString(),
            doctorName: title,
            note: 'Von Careena empfohlen',
            isRecommendation: true,
          ),
        );

    if (!context.mounted) return;

    await showDialog<void>(
      context: context,
      builder: (dialogContext) {
        return AlertDialog(
          title: Text(
            wasCreated
                ? 'Terminempfehlung hinzugefügt'
                : 'Terminempfehlung bereits vorhanden',
          ),
          content: Text(
            wasCreated
                ? 'Die Empfehlung wurde deiner Terminplanung hinzugefügt. Du kannst Datum und Uhrzeit dort später ergänzen.'
                : 'Diese Empfehlung ist bereits in deiner Terminplanung vorhanden.',
          ),
          actions: [
            TextButton(
              style: TextButton.styleFrom(
                foregroundColor: AppColors.careenaTeal,
              ),
              onPressed: () => Navigator.pop(dialogContext),
              child: const Text('Im Chat bleiben'),
            ),
            FilledButton(
              style: FilledButton.styleFrom(
                backgroundColor: AppColors.careenaTeal,
                foregroundColor: Colors.white,
              ),
              onPressed: () {
                Navigator.pop(dialogContext);
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => const AppointmentScreen(),
                  ),
                );
              },
              child: const Text('Zur Terminplanung'),
            ),
          ],
        );
      },
    );
  }
}
