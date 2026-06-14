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
    final appointmentDate = appointment.appointmentDate;
    final isPendingRecommendation =
        appointment.isRecommendation && appointmentDate == null;
    final shouldShowNote =
        appointment.note.isNotEmpty &&
        !(isPendingRecommendation &&
            appointment.note == 'Von Careena empfohlen');
    final colorScheme = Theme.of(context).colorScheme;

    return Card(
      elevation: isPendingRecommendation ? 0 : 3,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: isPendingRecommendation
            ? const BorderSide(color: AppColors.careenaTeal, width: 1.4)
            : BorderSide.none,
      ),
      color: appointment.isCompleted
          ? Theme.of(context).colorScheme.surfaceContainerHighest
          : isPendingRecommendation
              ? AppColors.careenaTeal.withValues(alpha: 0.08)
              : null,
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (isPendingRecommendation) ...[
              const Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    Icons.auto_awesome_outlined,
                    size: 16,
                    color: AppColors.careenaTeal,
                  ),
                  SizedBox(width: 6),
                  Text(
                    'Von Careena empfohlen',
                    style: TextStyle(
                      color: AppColors.careenaTeal,
                      fontSize: 13,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
            ],
            Row(
              children: [
                if (!isPendingRecommendation) ...[
                  Checkbox(
                    value: appointment.isCompleted,
                    activeColor: AppColors.careenaTeal,
                    onChanged: (_) => onToggleCompleted(),
                  ),
                  const SizedBox(width: 8),
                ],

                Expanded(
                  child: Text(
                    appointment.doctorName,
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,

                      color: appointment.isCompleted ? Colors.grey : null,

                      decoration: appointment.isCompleted
                          ? TextDecoration.lineThrough
                          : null,
                    ),
                  ),
                ),
                IconButton(
                  tooltip: 'Termin bearbeiten',
                  icon: const Icon(
                    Icons.edit_outlined,
                    color: AppColors.careenaTeal,
                  ),
                  onPressed: onEdit,
                ),

                const SizedBox(width: 4),

                DecoratedBox(
                  decoration: BoxDecoration(
                    color: Colors.red.withValues(alpha: 0.08),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: IconButton(
                    tooltip: isPendingRecommendation
                        ? 'Empfehlung verwerfen'
                        : 'Termin löschen',
                    icon: const Icon(
                      Icons.delete_outline,
                      color: Colors.red,
                      size: 22,
                    ),
                    onPressed: onDelete,
                  ),
                ),
              ],
            ),

            const SizedBox(height: 8),

            if (appointmentDate == null) ...[
              Row(
                children: [
                  const Icon(
                    Icons.event_note_outlined,
                    size: 18,
                    color: AppColors.careenaTeal,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    isPendingRecommendation
                        ? 'Terminempfehlung noch nicht vereinbart'
                        : 'Noch nicht vereinbart',
                    style: TextStyle(
                      color: isPendingRecommendation
                          ? AppColors.careenaTeal
                          : colorScheme.onSurface,
                      fontWeight: isPendingRecommendation
                          ? FontWeight.w600
                          : FontWeight.normal,
                    ),
                  ),
                ],
              ),
            ] else ...[
              Row(
                children: [
                  const Icon(
                    Icons.calendar_month,
                    size: 18,
                    color: AppColors.careenaTeal,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    '${appointmentDate.day}.'
                    '${appointmentDate.month}.'
                    '${appointmentDate.year}',
                  ),
                  const SizedBox(width: 16),
                  const Icon(
                    Icons.access_time,
                    size: 18,
                    color: AppColors.careenaTeal,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    '${appointmentDate.hour.toString().padLeft(2, '0')}:'
                    '${appointmentDate.minute.toString().padLeft(2, '0')} Uhr',
                  ),
                ],
              ),
            ],

            if (shouldShowNote) ...[
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

                  Expanded(child: Text(appointment.note)),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }
}
