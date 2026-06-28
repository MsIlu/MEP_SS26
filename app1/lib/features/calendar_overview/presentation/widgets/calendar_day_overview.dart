import 'package:app1/core/themes/app_colors.dart';
import 'package:app1/features/appointmentscreen/data/models/appointment.dart';
import 'package:app1/features/calendar_overview/presentation/utils/calendar_overview_date_utils.dart';
import 'package:app1/features/medication_plan/data/medication_entry.dart';
import 'package:app1/features/medication_plan/presentation/models/planned_medication_dose.dart';
import 'package:app1/features/symptom_diary/data/symptom_entry.dart';
import 'package:flutter/material.dart';

/// Lists all calendar entries for the selected day.
class CalendarDayOverview extends StatelessWidget {
  final DateTime date;
  final List<Appointment> appointments;
  final List<SymptomEntry> symptoms;
  final List<PlannedMedicationDose> medications;
  final ValueChanged<Appointment> onAppointmentTap;
  final ValueChanged<SymptomEntry> onSymptomTap;
  final ValueChanged<MedicationEntry> onMedicationTap;

  const CalendarDayOverview({
    super.key,
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
          calendarDateLabel(date),
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.w800,
          ),
        ),
        const SizedBox(height: 12),
        if (!hasAnyItems)
          const CalendarInfoCard(
            icon: Icons.event_available_outlined,
            title: 'Keine Einträge',
            lines: [
              CalendarInfoLine(
                text: 'Für diesen Tag sind keine Einträge vorhanden.',
                onTap: noopCalendarAction,
              ),
            ],
          )
        else ...[
          CalendarInfoCard(
            icon: Icons.event_outlined,
            title: 'Termine',
            lines: appointments.map((appointment) {
              final date = appointment.appointmentDate;
              final time = date == null
                  ? ''
                  : '${twoDigits(date.hour)}:${twoDigits(date.minute)} ';
              return CalendarInfoLine(
                text: '$time${appointment.doctorName}',
                onTap: () => onAppointmentTap(appointment),
              );
            }).toList(),
          ),
          CalendarInfoCard(
            icon: Icons.menu_book_outlined,
            title: 'Symptome',
            lines: symptoms
                .map(
                  (entry) => CalendarInfoLine(
                    text: symptomLine(entry),
                    onTap: () => onSymptomTap(entry),
                  ),
                )
                .toList(),
          ),
          CalendarInfoCard(
            icon: Icons.medication_outlined,
            title: 'Medikamente',
            lines: medications.map((dose) {
              final time = dose.intakeTime;
              final suffix = dose.entry.intakeTimes.length > 1
                  ? ' (${dose.doseIndex + 1}. Einnahme)'
                  : '';
              return CalendarInfoLine(
                text:
                    '${twoDigits(time.hour)}:${twoDigits(time.minute)} '
                    '${dose.entry.name} ${dose.entry.dose}$suffix',
                onTap: () => onMedicationTap(dose.entry),
              );
            }).toList(),
          ),
        ],
      ],
    );
  }
}

class CalendarInfoCard extends StatefulWidget {
  final IconData icon;
  final String title;
  final List<CalendarInfoLine> lines;

  const CalendarInfoCard({
    super.key,
    required this.icon,
    required this.title,
    required this.lines,
  });

  @override
  State<CalendarInfoCard> createState() => _CalendarInfoCardState();
}

class _CalendarInfoCardState extends State<CalendarInfoCard> {
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

class CalendarInfoLine {
  final String text;
  final VoidCallback onTap;

  const CalendarInfoLine({required this.text, required this.onTap});
}

class _CalendarInfoRow extends StatelessWidget {
  final CalendarInfoLine line;

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
            const Icon(
              Icons.chevron_right,
              size: 18,
              color: AppColors.careenaTeal,
            ),
          ],
        ),
      ),
    );
  }
}

String symptomLine(SymptomEntry entry) {
  final bodyArea = entry.bodyArea.trim();
  if (bodyArea.isEmpty) return entry.symptom;
  return '${entry.symptom} ($bodyArea)';
}

void noopCalendarAction() {}
