import 'package:app1/core/themes/app_colors.dart';
import 'package:flutter/material.dart';

import '../utils/symptom_intensity.dart';

/// Final step of the symptom form: intensity and optional notes.
class SymptomDetailsStep extends StatelessWidget {
  final int intensity;
  final double temperatureC;
  final bool useTemperature;
  final TextEditingController noteController;
  final ValueChanged<int> onIntensityChanged;
  final ValueChanged<double> onTemperatureChanged;

  const SymptomDetailsStep({
    super.key,
    required this.intensity,
    this.temperatureC = 37.0,
    this.useTemperature = false,
    required this.noteController,
    required this.onIntensityChanged,
    required this.onTemperatureChanged,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    final intensityColor = useTemperature
        ? _temperatureColor(temperatureC)
        : SymptomIntensity.color(intensity);

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
              _ScaleHeader(
                title: useTemperature ? 'Temperatur' : 'Intensität',
                value: useTemperature
                    ? '${temperatureC.toStringAsFixed(1)} °C · ${_temperatureLabel(temperatureC)}'
                    : '$intensity/10 · ${SymptomIntensity.label(intensity)}',
                color: intensityColor,
              ),
              if (useTemperature)
                SliderTheme(
                  data: SliderTheme.of(context).copyWith(
                    trackHeight: 3,
                    activeTickMarkColor: AppColors.transparent,
                    inactiveTickMarkColor: AppColors.transparent,
                    thumbShape: const RoundSliderThumbShape(
                      enabledThumbRadius: 15,
                    ),
                    overlayShape: const RoundSliderOverlayShape(
                      overlayRadius: 24,
                    ),
                  ),
                  child: Slider(
                    value: temperatureC,
                    min: 36,
                    max: 42,
                    activeColor: intensityColor,
                    inactiveColor: intensityColor.withValues(alpha: 0.25),
                    label: '${temperatureC.toStringAsFixed(1)} °C',
                    onChanged: (value) =>
                        onTemperatureChanged((value * 10).round() / 10),
                  ),
                )
              else
                Slider(
                  value: intensity.toDouble(),
                  min: 1,
                  max: 10,
                  divisions: 9,
                  activeColor: intensityColor,
                  label: intensity.toString(),
                  onChanged: (value) => onIntensityChanged(value.round()),
                ),
              _ScaleLabels(useTemperature: useTemperature),
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

class _ScaleHeader extends StatelessWidget {
  final String title;
  final String value;
  final Color color;

  const _ScaleHeader({
    required this.title,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: Text(
            title,
            style: TextStyle(
              color: Theme.of(context).colorScheme.onSurface,
              fontWeight: FontWeight.w800,
            ),
          ),
        ),
        Expanded(
          child: Align(
            alignment: Alignment.centerRight,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
              decoration: BoxDecoration(
                color: color.withValues(alpha: 0.18),
                borderRadius: BorderRadius.circular(999),
              ),
              child: Text(
                value,
                overflow: TextOverflow.ellipsis,
                textAlign: TextAlign.right,
                style: TextStyle(color: color, fontWeight: FontWeight.w900),
              ),
            ),
          ),
        ),
      ],
    );
  }
}

class _ScaleLabels extends StatelessWidget {
  final bool useTemperature;

  const _ScaleLabels({required this.useTemperature});

  @override
  Widget build(BuildContext context) {
    final labels = useTemperature
        ? const ['36,0 °C', '37,5 °C', '42,0 °C']
        : const ['leicht', 'mittel', 'stark'];

    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        for (final label in labels)
          Text(label, style: const TextStyle(fontSize: 12)),
      ],
    );
  }
}

String _temperatureLabel(double value) {
  if (value >= 38.1) return 'Fieber';
  if (value >= 37.5) return 'erhöht';
  if (value >= 36.7) return 'normal';
  return 'niedrig';
}

Color _temperatureColor(double value) {
  if (value >= 38.1) return AppColors.symptomIntensityHigh;
  if (value >= 37.5) return AppColors.symptomIntensityMedium;
  return AppColors.symptomIntensityLow;
}
