import 'package:app1/core/themes/app_colors.dart';
import 'package:app1/features/authscreen/domain/models/auth_response.dart';
import 'package:flutter/material.dart';

class AppointmentProfileFilter extends StatelessWidget {
  final List<AuthProfile> profiles;
  final int? selectedProfileId;
  final bool showAllProfiles;
  final VoidCallback onShowAll;
  final ValueChanged<int> onProfileSelected;

  const AppointmentProfileFilter({
    super.key,
    required this.profiles,
    required this.selectedProfileId,
    required this.showAllProfiles,
    required this.onShowAll,
    required this.onProfileSelected,
  });

  @override
  Widget build(BuildContext context) {
    if (profiles.length < 2) {
      return const SizedBox.shrink();
    }

    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: [
          _ProfileChip(
            label: 'Alle Profile',
            selected: showAllProfiles,
            onSelected: onShowAll,
          ),
          for (final profile in profiles)
            _ProfileChip(
              label: profile.displayName,
              selected:
                  !showAllProfiles &&
                  selectedProfileId == profile.id,
              onSelected: () => onProfileSelected(profile.id),
            ),
        ],
      ),
    );
  }
}

class _ProfileChip extends StatelessWidget {
  final String label;
  final bool selected;
  final VoidCallback onSelected;

  const _ProfileChip({
    required this.label,
    required this.selected,
    required this.onSelected,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(right: 8),
      child: ChoiceChip(
        label: Text(label),
        selected: selected,
        selectedColor: AppColors.careenaTeal,
        showCheckmark: false,
        labelStyle: TextStyle(
          color: selected ? Colors.white : null,
          fontWeight:
              selected ? FontWeight.bold : FontWeight.normal,
        ),
        onSelected: (_) => onSelected(),
      ),
    );
  }
}