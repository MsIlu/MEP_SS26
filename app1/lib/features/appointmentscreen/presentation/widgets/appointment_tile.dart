import 'package:flutter/material.dart';
import 'package:app1/core/themes/app_colors.dart';
import '../../data/models/appointment.dart';

class AppointmentTile extends StatelessWidget {
  final Appointment appointment;
  final VoidCallback onToggleCompleted;
  final VoidCallback onDelete;
  final VoidCallback onEdit;

  const AppointmentTile({
    super.key,
    required this.appointment,
    required this.onToggleCompleted,
    required this.onDelete,
    required this.onEdit,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 3,

  color: appointment.isCompleted

      ? Theme.of(context).colorScheme.surfaceContainerHighest

      : null,
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
  children: [
    Checkbox(
      value: appointment.isCompleted,
      activeColor: AppColors.careenaTeal,
      onChanged: (_) => onToggleCompleted(),
    ),

    

    const SizedBox(width: 8),

    Expanded(
      child: Text(
  appointment.doctorName,
  style: TextStyle(
    fontSize: 20,
    fontWeight: FontWeight.bold,

    color: appointment.isCompleted
        ? Colors.grey
        : null,

    decoration: appointment.isCompleted
        ? TextDecoration.lineThrough
        : null,
  ),
),
    ),
    IconButton(
  icon: const Icon(
    Icons.edit_outlined,
    color: AppColors.careenaTeal,
  ),
  onPressed: onEdit,
),

IconButton(
  icon: const Icon(
    Icons.delete_outline,
    color: Colors.red,
  ),
  onPressed: onDelete,
),
  ],
),

            const SizedBox(height: 8),

            Row(
              children: [
                const Icon(
                  Icons.calendar_month,
                  size: 18,
                  color: AppColors.careenaTeal,
                ),
                const SizedBox(width: 8),
                Text(
                  '${appointment.appointmentDate.day}.'
                  '${appointment.appointmentDate.month}.'
                  '${appointment.appointmentDate.year}',
                ),
              ],
            ),

            const SizedBox(height: 8),

            Row(
              children: [
                const Icon(
                  Icons.access_time,
                  size: 18,
                  color: AppColors.careenaTeal,
                ),
                const SizedBox(width: 8),
                Text(
                  '${appointment.appointmentDate.hour.toString().padLeft(2, '0')}:'
                  '${appointment.appointmentDate.minute.toString().padLeft(2, '0')} Uhr',
                ),
              ],
            ),

            if (appointment.note.isNotEmpty) ...[
              const SizedBox(height: 8),

              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Icon(
                    Icons.note_alt_outlined,
                    size: 18,
                    color: AppColors.careenaTeal,
                  ),
                  const SizedBox(width: 8),

                  Expanded(
                    child: Text(
                      appointment.note,
                    ),
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }
}