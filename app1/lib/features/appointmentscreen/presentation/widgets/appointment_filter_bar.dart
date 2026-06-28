import 'package:flutter/material.dart';
import 'package:app1/core/themes/app_colors.dart';

class AppointmentFilterBar extends StatelessWidget {
  final String selectedFilter;
  final ValueChanged<String> onFilterChanged;

  const AppointmentFilterBar({
    super.key,
    required this.selectedFilter,
    required this.onFilterChanged,
  });

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: [
          _buildFilterChip('Alle'),
          _buildFilterChip('Kommend'),
          _buildFilterChip('Vergangen'),
          _buildFilterChip('Erledigt'),
        ],
      ),
    );
  }

  Widget _buildFilterChip(String label) {
    final isSelected = selectedFilter == label;

    return Padding(
      padding: const EdgeInsets.only(right: 8),
      child: ChoiceChip(
        label: Text(label),
        selected: isSelected,
        selectedColor: AppColors.careenaTeal,
        checkmarkColor: AppColors.white,
        labelStyle: TextStyle(
          color: isSelected ? AppColors.white : null,
        ),
        onSelected: (_) {
          onFilterChanged(label);
        },
      ),
    );
  }
}