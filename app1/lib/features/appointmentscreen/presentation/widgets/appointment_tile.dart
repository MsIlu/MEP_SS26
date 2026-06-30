import 'package:flutter/material.dart';
import 'package:app1/core/themes/app_colors.dart';
import '../../data/models/appointment.dart';

class AppointmentTile extends StatefulWidget {
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
  State<AppointmentTile> createState() => _AppointmentTileState();
}

class _AppointmentTileState extends State<AppointmentTile> {
  bool isNoteExpanded = false;

  @override
  Widget build(BuildContext context) {
    final appointment = widget.appointment;
    final appointmentDate = appointment.appointmentDate;
    final isPendingRecommendation =
        appointment.isRecommendation && appointmentDate == null;
    final shouldShowNote =
        appointment.note.isNotEmpty &&
        !(isPendingRecommendation &&
            appointment.note == 'Von Careena empfohlen');
    final colorScheme = Theme.of(context).colorScheme;
    final appointmentLabel = _semanticLabel(
      appointment: appointment,
      appointmentDate: appointmentDate,
      isPendingRecommendation: isPendingRecommendation,
      shouldShowNote: shouldShowNote,
    );

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
      child: Semantics(
        container: true,
        label: appointmentLabel,
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
                    Semantics(
                      label: appointment.isCompleted
                          ? 'Termin ${appointment.doctorName} als offen markieren'
                          : 'Termin ${appointment.doctorName} als erledigt markieren',
                      checked: appointment.isCompleted,
                      onTap: widget.onToggleCompleted,
                      child: ExcludeSemantics(
                        child: Checkbox(
                          value: appointment.isCompleted,
                          activeColor: AppColors.careenaTeal,
                          onChanged: (_) => widget.onToggleCompleted(),
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                  ],

                  Expanded(
                    child: Text(
                      appointment.doctorName,
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,

                        color: appointment.isCompleted ? AppColors.grey : null,

                        decoration: appointment.isCompleted
                            ? TextDecoration.lineThrough
                            : null,
                      ),
                    ),
                  ),
                  Semantics(
                    button: true,
                    label: 'Termin ${appointment.doctorName} bearbeiten',
                    onTap: widget.onEdit,
                    child: ExcludeSemantics(
                      child: IconButton(
                        tooltip: 'Termin ${appointment.doctorName} bearbeiten',
                        icon: const Icon(
                          Icons.edit_outlined,
                          color: AppColors.careenaTeal,
                        ),
                        onPressed: widget.onEdit,
                      ),
                    ),
                  ),

                  const SizedBox(width: 4),

                  DecoratedBox(
                    decoration: BoxDecoration(
                      color: AppColors.red.withValues(alpha: 0.08),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Semantics(
                      button: true,
                      label: isPendingRecommendation
                          ? 'Empfehlung ${appointment.doctorName} verwerfen'
                          : 'Termin ${appointment.doctorName} löschen',
                      onTap: widget.onDelete,
                      child: ExcludeSemantics(
                        child: IconButton(
                          tooltip: isPendingRecommendation
                              ? 'Empfehlung ${appointment.doctorName} verwerfen'
                              : 'Termin ${appointment.doctorName} löschen',
                          icon: const Icon(
                            Icons.delete_outline,
                            color: AppColors.red,
                            size: 22,
                          ),
                          onPressed: widget.onDelete,
                        ),
                      ),
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
                    Expanded(
                      child: _ExpandableNote(
                        text: appointment.note,
                        isExpanded: isNoteExpanded,
                        onToggle: () {
                          setState(() {
                            isNoteExpanded = !isNoteExpanded;
                          });
                        },
                      ),
                    ),
                  ],
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  String _semanticLabel({
    required Appointment appointment,
    required DateTime? appointmentDate,
    required bool isPendingRecommendation,
    required bool shouldShowNote,
  }) {
    final parts = <String>[];
    parts.add(
      isPendingRecommendation
          ? 'Terminempfehlung: ${appointment.doctorName}'
          : 'Termin: ${appointment.doctorName}',
    );
    if (appointment.isCompleted) {
      parts.add('Erledigt');
    }
    if (appointmentDate == null) {
      parts.add(
        isPendingRecommendation
            ? 'Noch nicht vereinbart'
            : 'Kein Datum vereinbart',
      );
    } else {
      parts.add(
        'Am ${appointmentDate.day}.${appointmentDate.month}.${appointmentDate.year}',
      );
      parts.add(
        'um ${appointmentDate.hour.toString().padLeft(2, '0')}:${appointmentDate.minute.toString().padLeft(2, '0')} Uhr',
      );
    }
    if (shouldShowNote) {
      parts.add('Notiz: ${appointment.note}');
    }
    return parts.join('. ');
  }
}

class _ExpandableNote extends StatelessWidget {
  final String text;
  final bool isExpanded;
  final VoidCallback onToggle;

  const _ExpandableNote({
    required this.text,
    required this.isExpanded,
    required this.onToggle,
  });

  @override
  Widget build(BuildContext context) {
    final isLongNote = text.length > 90;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          text,
          maxLines: isExpanded ? null : 1,
          overflow: isExpanded ? TextOverflow.visible : TextOverflow.ellipsis,
        ),
        if (isLongNote)
          Semantics(
            button: true,
            label: isExpanded
                ? 'Notiz gekürzt anzeigen'
                : 'Notiz vollständig anzeigen',
            onTap: onToggle,
            child: ExcludeSemantics(
              child: TextButton(
                style: TextButton.styleFrom(
                  foregroundColor: AppColors.careenaTeal,
                  padding: EdgeInsets.zero,
                  minimumSize: const Size(0, 32),
                  tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                ),
                onPressed: onToggle,
                child: Text(isExpanded ? 'Weniger anzeigen' : 'Mehr anzeigen'),
              ),
            ),
          ),
      ],
    );
  }
}
