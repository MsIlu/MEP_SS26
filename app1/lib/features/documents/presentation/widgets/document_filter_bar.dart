import 'package:app1/core/themes/app_colors.dart';
import 'package:flutter/material.dart';

import '../../data/models/document_entry.dart';

class DocumentFilterBar extends StatelessWidget {
  final DocumentCategory? selectedCategory;
  final ValueChanged<DocumentCategory?> onSelected;

  const DocumentFilterBar({
    super.key,
    required this.selectedCategory,
    required this.onSelected,
  });

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: [
          _FilterChip(
            label: 'Alle',
            selected: selectedCategory == null,
            onSelected: () => onSelected(null),
          ),
          for (final category in DocumentCategory.values)
            _FilterChip(
              label: category.label,
              selected: selectedCategory == category,
              onSelected: () => onSelected(category),
            ),
        ],
      ),
    );
  }
}

class _FilterChip extends StatelessWidget {
  final String label;
  final bool selected;
  final VoidCallback onSelected;

  const _FilterChip({
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
        checkmarkColor: Colors.white,
        labelStyle: TextStyle(color: selected ? Colors.white : null),
        onSelected: (_) => onSelected(),
      ),
    );
  }
}
