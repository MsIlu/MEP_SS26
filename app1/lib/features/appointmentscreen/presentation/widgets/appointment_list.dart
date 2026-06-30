import 'package:app1/core/themes/app_colors.dart';
import 'package:app1/core/widgets/careena_empty_state.dart';
import 'package:app1/features/authscreen/domain/models/auth_response.dart';
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
  final List<AuthProfile> profiles;
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
    this.profiles = const [],
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

        if (showAllProfiles && profiles.length > 1) {
          return _GroupedAppointmentList(
            profiles: profiles,
            appointments: visibleAppointments,
            selectedFilter: selectedFilter,
            shrinkWrap: shrinkWrap,
            onToggleCompleted: onToggleCompleted,
            onDelete: onDelete,
            onEdit: onEdit,
          );
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
          children: _AppointmentSectionContent(
            sections: sections,
            onToggleCompleted: onToggleCompleted,
            onDelete: onDelete,
            onEdit: onEdit,
          ).children,
        );
      },
    );
  }
}

class _GroupedAppointmentList extends StatelessWidget {
  final List<AuthProfile> profiles;
  final List<Appointment> appointments;
  final String selectedFilter;
  final bool shrinkWrap;
  final ValueChanged<Appointment> onToggleCompleted;
  final ValueChanged<Appointment> onDelete;
  final ValueChanged<Appointment> onEdit;

  const _GroupedAppointmentList({
    required this.profiles,
    required this.appointments,
    required this.selectedFilter,
    required this.shrinkWrap,
    required this.onToggleCompleted,
    required this.onDelete,
    required this.onEdit,
  });

  @override
  Widget build(BuildContext context) {
    final sections = <_ProfileAppointmentSectionData>[];

    for (final profile in profiles) {
      final profileAppointments = appointments
          .where((appointment) => appointment.profileId == profile.id)
          .toList();
      if (profileAppointments.isEmpty) continue;

      final appointmentSections = buildAppointmentSections(
        profileAppointments,
        selectedFilter,
      );
      if (appointmentSections.isEmpty) continue;

      sections.add(
        _ProfileAppointmentSectionData(
          profile: profile,
          appointmentSections: appointmentSections,
          totalCount:
              appointmentSections.recommendedAppointments.length +
              appointmentSections.plannedAppointments.length,
        ),
      );
    }

    if (sections.isEmpty) {
      return _EmptyFilterState(shrinkWrap: shrinkWrap);
    }

    return ListView(
      shrinkWrap: shrinkWrap,
      physics: shrinkWrap ? const NeverScrollableScrollPhysics() : null,
      children: [
        for (var index = 0; index < sections.length; index++) ...[
          _ProfileAppointmentSection(
            section: sections[index],
            onToggleCompleted: onToggleCompleted,
            onDelete: onDelete,
            onEdit: onEdit,
          ),
          if (index < sections.length - 1) const SizedBox(height: 12),
        ],
      ],
    );
  }
}

class _ProfileAppointmentSectionData {
  final AuthProfile profile;
  final AppointmentSections appointmentSections;
  final int totalCount;

  const _ProfileAppointmentSectionData({
    required this.profile,
    required this.appointmentSections,
    required this.totalCount,
  });
}

class _ProfileAppointmentSection extends StatelessWidget {
  final _ProfileAppointmentSectionData section;
  final ValueChanged<Appointment> onToggleCompleted;
  final ValueChanged<Appointment> onDelete;
  final ValueChanged<Appointment> onEdit;

  const _ProfileAppointmentSection({
    required this.section,
    required this.onToggleCompleted,
    required this.onDelete,
    required this.onEdit,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Theme(
      data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
      child: ExpansionTile(
        tilePadding: const EdgeInsets.symmetric(horizontal: 14),
        childrenPadding: const EdgeInsets.only(bottom: 12),
        initiallyExpanded: true,
        collapsedShape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(10),
        ),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        collapsedBackgroundColor: AppColors.careenaTeal.withValues(alpha: 0.08),
        backgroundColor: AppColors.careenaTeal.withValues(alpha: 0.08),
        title: Text(
          _profileSectionTitle(section.profile),
          style: TextStyle(
            color: colorScheme.onSurface,
            fontWeight: FontWeight.w800,
          ),
        ),
        subtitle: Text(
          '${section.totalCount} ${section.totalCount == 1 ? 'Termin' : 'Termine'}',
        ),
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(0, 8, 0, 0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: _AppointmentSectionContent(
                sections: section.appointmentSections,
                onToggleCompleted: onToggleCompleted,
                onDelete: onDelete,
                onEdit: onEdit,
              ).children,
            ),
          ),
        ],
      ),
    );
  }

  String _profileSectionTitle(AuthProfile profile) {
    if (profile.profileType == 'self') {
      return 'Hauptprofil';
    }

    return profile.displayName;
  }
}

class _AppointmentSectionContent {
  final AppointmentSections sections;
  final ValueChanged<Appointment> onToggleCompleted;
  final ValueChanged<Appointment> onDelete;
  final ValueChanged<Appointment> onEdit;

  const _AppointmentSectionContent({
    required this.sections,
    required this.onToggleCompleted,
    required this.onDelete,
    required this.onEdit,
  });

  List<Widget> get children {
    return [
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
        if (sections.plannedAppointments.isNotEmpty) const SizedBox(height: 12),
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
    ];
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
