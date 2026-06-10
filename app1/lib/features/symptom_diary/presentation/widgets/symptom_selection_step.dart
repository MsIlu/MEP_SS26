import 'package:app1/core/themes/app_colors.dart';
import 'package:flutter/material.dart';

/// First step of the symptom form: choose or type the symptom name.
class SymptomSelectionStep extends StatelessWidget {
  final List<String> suggestions;
  final List<String> filteredSuggestions;
  final TextEditingController controller;
  final ValueChanged<String> onChanged;
  final ValueChanged<String> onSelected;
  final VoidCallback onSubmitted;

  const SymptomSelectionStep({
    super.key,
    required this.suggestions,
    required this.filteredSuggestions,
    required this.controller,
    required this.onChanged,
    required this.onSelected,
    required this.onSubmitted,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final selectedSymptom = controller.text.trim();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          'Wähle etwas aus oder schreibe frei.',
          style: TextStyle(
            color: colorScheme.onSurfaceVariant,
            fontSize: 13,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 12),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: suggestions.map((symptom) {
            final isSelected = selectedSymptom == symptom;

            return ChoiceChip(
              label: Text(symptom),
              selected: isSelected,
              selectedColor: AppColors.careenaBubbleBackground,
              checkmarkColor: AppColors.careenaTeal,
              onSelected: (_) => onSelected(symptom),
            );
          }).toList(),
        ),
        const SizedBox(height: 22),
        _SymptomTextField(
          controller: controller,
          hasSymptom: selectedSymptom.isNotEmpty,
          colorScheme: colorScheme,
          onChanged: onChanged,
          onSubmitted: onSubmitted,
        ),
        if (filteredSuggestions.isNotEmpty) ...[
          const SizedBox(height: 8),
          _InlineSymptomSuggestions(
            suggestions: filteredSuggestions,
            onSelected: onSelected,
          ),
        ],
      ],
    );
  }
}

class _SymptomTextField extends StatelessWidget {
  final TextEditingController controller;
  final bool hasSymptom;
  final ColorScheme colorScheme;
  final ValueChanged<String> onChanged;
  final VoidCallback onSubmitted;

  const _SymptomTextField({
    required this.controller,
    required this.hasSymptom,
    required this.colorScheme,
    required this.onChanged,
    required this.onSubmitted,
  });

  @override
  Widget build(BuildContext context) {
    final quietColor = colorScheme.onSurfaceVariant.withValues(
      alpha: hasSymptom ? 0.86 : 0.58,
    );

    return TextField(
      controller: controller,
      textInputAction: TextInputAction.next,
      onChanged: onChanged,
      onSubmitted: (_) => onSubmitted(),
      decoration: InputDecoration(
        labelText: 'Symptom',
        hintText: 'z. B. Kopfschmerzen',
        prefixIcon: Icon(
          Icons.sick_outlined,
          color: colorScheme.onSurfaceVariant.withValues(alpha: 0.64),
        ),
        labelStyle: TextStyle(
          color: quietColor,
          fontWeight: hasSymptom ? FontWeight.w600 : FontWeight.w400,
        ),
        floatingLabelStyle: TextStyle(
          color: hasSymptom
              ? AppColors.careenaTeal
              : colorScheme.onSurfaceVariant.withValues(alpha: 0.68),
          fontWeight: FontWeight.w600,
        ),
        hintStyle: TextStyle(
          color: colorScheme.onSurfaceVariant.withValues(alpha: 0.45),
          fontWeight: FontWeight.w400,
        ),
      ),
    );
  }
}

class _InlineSymptomSuggestions extends StatelessWidget {
  final List<String> suggestions;
  final ValueChanged<String> onSelected;

  const _InlineSymptomSuggestions({
    required this.suggestions,
    required this.onSelected,
  });

  @override
  Widget build(BuildContext context) {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: suggestions.map((symptom) {
        return ActionChip(
          avatar: const Icon(Icons.north_west, size: 16),
          label: Text(symptom),
          onPressed: () => onSelected(symptom),
          side: BorderSide(
            color: AppColors.careenaTeal.withValues(alpha: 0.35),
          ),
          backgroundColor: AppColors.careenaBubbleBackground.withValues(
            alpha: 0.72,
          ),
        );
      }).toList(),
    );
  }
}
