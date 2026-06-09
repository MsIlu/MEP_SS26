import 'package:app1/core/themes/app_colors.dart';
import 'package:flutter/material.dart';

import '../utils/symptom_intensity.dart';

/// Final step of the symptom form: intensity and optional notes.
class SymptomDetailsStep extends StatelessWidget {
  final int intensity;
  final TextEditingController noteController;
  final ValueChanged<int> onIntensityChanged;

  const SymptomDetailsStep({
    super.key,
    required this.intensity,
    required this.noteController,
    required this.onIntensityChanged,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    final intensityColor = SymptomIntensity.color(intensity);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Container(
          padding: const EdgeInsets.fromLTRB(12, 12, 12, 6),
          decoration: BoxDecoration(
            color: isDarkMode
                ? colorScheme.surfaceContainerHighest.withValues(alpha: 0.35)
                : AppColors.careenaBubbleBackground.withValues(alpha: 0.5),
            borderRadius: BorderRadius.circular(16),
          ),
          child: Column(
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      'Intensität',
                      style: TextStyle(
                        color: colorScheme.onSurface,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 10,
                      vertical: 5,
                    ),
                    decoration: BoxDecoration(
                      color: intensityColor.withValues(alpha: 0.18),
                      borderRadius: BorderRadius.circular(999),
                    ),
                    child: Text(
                      '$intensity/10 · ${SymptomIntensity.label(intensity)}',
                      style: TextStyle(
                        color: intensityColor,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                  ),
                ],
              ),
              Slider(
                value: intensity.toDouble(),
                min: 1,
                max: 10,
                divisions: 9,
                activeColor: intensityColor,
                label: intensity.toString(),
                onChanged: (value) => onIntensityChanged(value.round()),
              ),
              const Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('leicht', style: TextStyle(fontSize: 12)),
                  Text('mittel', style: TextStyle(fontSize: 12)),
                  Text('stark', style: TextStyle(fontSize: 12)),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 14),
        TextField(
          controller: noteController,
          minLines: 2,
          maxLines: 4,
          textInputAction: TextInputAction.done,
          decoration: const InputDecoration(
            labelText: 'Notiz (optional)',
            hintText: 'Was ist aufgefallen? Auslöser, Verlauf, Ort...',
            prefixIcon: Icon(Icons.notes_outlined),
          ),
        ),
      ],
    );
  }
}
