import 'package:app1/core/themes/app_colors.dart';
import 'package:app1/core/widgets/careena_empty_state.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

import '../../data/models/appointment.dart';
import '../utils/appointment_filtering.dart';
import 'appointment_empty_state.dart';
import 'appointment_tile.dart';

/// Renders filtered appointments and keeps list section logic out of the screen.
class AppointmentList extends StatelessWidget {
  final ValueListenable<List<Appointment>> appointmentsListenable;
  final String selectedFilter;
  final int? selectedProfileId;
  final bool showAllProfiles;
  final bool shrinkWrap;
  final ValueChanged<Appointment> onToggleCompleted;
  final ValueChanged<Appointment> onDelete;
  final ValueChanged<Appointment> onEdit;

  const AppointmentList({
    super.key,
    required this.appointmentsListenable,
    required this.selectedFilter,
    this.selectedProfileId,
    this.showAllProfiles = true,
    required this.shrinkWrap,
    required this.onToggleCompleted,
    required this.onDelete,
    required this.onEdit,
  });

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<List<Appointment>>(
      valueListenable: appointmentsListenable,
      builder: (context, appointments, child) {
        final visibleAppointments = showAllProfiles
            ? appointments
            : appointments
                  .where(
                    (appointment) => appointment.profileId == selectedProfileId,
                  )
                  .toList();

        if (visibleAppointments.isEmpty) {
          return shrinkWrap
              ? const SizedBox(height: 180, child: AppointmentEmptyState())
              : const AppointmentEmptyState();
        }

        final sections = buildAppointmentSections(
          visibleAppointments,
          selectedFilter,
        );
        if (sections.isEmpty) {
          return _EmptyFilterState(shrinkWrap: shrinkWrap);
        }

        return ListView(
          shrinkWrap: shrinkWrap,
          physics: shrinkWrap ? const NeverScrollableScrollPhysics() : null,
          children: [
            if (sections.recommendedAppointments.isNotEmpty) ...[
              const _AppointmentSectionHeader(
                icon: Icons.auto_awesome_outlined,
                title: 'Empfohlene nächste Schritte',
                subtitle:
                    'Von Careena vorgeschlagene Termine, die du noch eintragen kannst.',
              ),
              const SizedBox(height: 8),
              for (final appointment in sections.recommendedAppointments)
                _AppointmentListTile(
                  appointment: appointment,
                  onToggleCompleted: onToggleCompleted,
                  onDelete: onDelete,
                  onEdit: onEdit,
                ),
              if (sections.plannedAppointments.isNotEmpty)
                const SizedBox(height: 12),
            ],
            if (sections.plannedAppointments.isNotEmpty) ...[
              if (sections.recommendedAppointments.isNotEmpty) ...[
                const _AppointmentSectionHeader(
                  icon: Icons.event_available_outlined,
                  title: 'Geplante Termine',
                ),
                const SizedBox(height: 8),
              ],
              for (final appointment in sections.plannedAppointments)
                _AppointmentListTile(
                  appointment: appointment,
                  onToggleCompleted: onToggleCompleted,
                  onDelete: onDelete,
                  onEdit: onEdit,
                ),
            ],
          ],
        );
      },
    );
  }
}

class _AppointmentListTile extends StatelessWidget {
  final Appointment appointment;
  final ValueChanged<Appointment> onToggleCompleted;
  final ValueChanged<Appointment> onDelete;
  final ValueChanged<Appointment> onEdit;

  const _AppointmentListTile({
    required this.appointment,
    required this.onToggleCompleted,
    required this.onDelete,
    required this.onEdit,
  });

  @override
  Widget build(BuildContext context) {
    return AppointmentTile(
      appointment: appointment,
      onToggleCompleted: () => onToggleCompleted(appointment),
      onDelete: () => onDelete(appointment),
      onEdit: () => onEdit(appointment),
    );
  }
}

class _EmptyFilterState extends StatelessWidget {
  final bool shrinkWrap;

  const _EmptyFilterState({required this.shrinkWrap});

  @override
  Widget build(BuildContext context) {
    const emptyFilter = CareenaEmptyState(
      icon: Icons.filter_alt_off_outlined,
      title: 'Keine Termine in diesem Filter',
      message: 'Passe den Filter an, um weitere Termine zu sehen.',
    );

    return shrinkWrap
        ? const SizedBox(height: 180, child: emptyFilter)
        : emptyFilter;
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
