import 'package:app1/core/themes/app_colors.dart';
import 'package:flutter/material.dart';

import '../utils/symptom_intensity.dart';

/// Final step of the symptom form: intensity and optional notes.
class SymptomDetailsStep extends StatelessWidget {
  final int intensity;
  final bool usesTemperature;
  final double temperature;
  final TextEditingController noteController;
  final ValueChanged<int> onIntensityChanged;
  final ValueChanged<double> onTemperatureChanged;

  const SymptomDetailsStep({
    super.key,
    required this.intensity,
    required this.usesTemperature,
    required this.temperature,
    required this.noteController,
    required this.onIntensityChanged,
    required this.onTemperatureChanged,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    final statusColor = usesTemperature
        ? _temperatureColor(temperature)
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
              Row(
                children: [
                  Expanded(
                    child: Text(
                      usesTemperature ? 'Temperatur' : 'Intensität',
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
                      color: statusColor.withValues(alpha: 0.18),
                      borderRadius: BorderRadius.circular(999),
                    ),
                    child: Text(
                      usesTemperature
                          ? '${_formatTemperature(temperature)} °C · ${_temperatureLabel(temperature)}'
                          : '$intensity/10 · ${SymptomIntensity.label(intensity)}',
                      style: TextStyle(
                        color: statusColor,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                  ),
                ],
              ),
              if (usesTemperature)
                _TemperatureInput(
                  temperature: temperature,
                  activeColor: statusColor,
                  onChanged: onTemperatureChanged,
                )
              else
                _IntensityInput(
                  intensity: intensity,
                  activeColor: statusColor,
                  onChanged: onIntensityChanged,
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

  Color _temperatureColor(double temperature) {
    if (temperature > 38.0) {
      return AppColors.symptomIntensityHigh;
    }
    if (temperature >= 37.5) {
      return AppColors.symptomIntensityMedium;
    }
    return AppColors.symptomIntensityNone;
  }

  String _formatTemperature(double value) {
    return value.toStringAsFixed(1).replaceAll('.', ',');
  }

  String _temperatureLabel(double temperature) {
    if (temperature > 38.0) {
      return 'Fieber';
    }
    if (temperature >= 37.5) {
      return 'erhöht';
    }
    return 'normal';
  }
}

class _IntensityInput extends StatelessWidget {
  final int intensity;
  final Color activeColor;
  final ValueChanged<int> onChanged;

  const _IntensityInput({
    required this.intensity,
    required this.activeColor,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Slider(
          value: intensity.toDouble(),
          min: 1,
          max: 10,
          divisions: 9,
          activeColor: activeColor,
          label: intensity.toString(),
          onChanged: (value) => onChanged(value.round()),
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
    );
  }
}

class _TemperatureInput extends StatelessWidget {
  static const _minTemperature = 36.0;
  static const _maxTemperature = 42.0;
  static const _ticks = [
    _TemperatureTick(36.0, '36,0 °C'),
    _TemperatureTick(36.5, '36,5'),
    _TemperatureTick(37.0, '37,0'),
    _TemperatureTick(37.5, '37,5'),
    _TemperatureTick(38.0, '38,0'),
    _TemperatureTick(38.5, '38,5'),
    _TemperatureTick(39.0, '39,0'),
    _TemperatureTick(39.5, '39,5'),
    _TemperatureTick(40.0, '40,0'),
    _TemperatureTick(40.5, '40,5'),
    _TemperatureTick(41.0, '41,0'),
    _TemperatureTick(41.5, '41,5'),
    _TemperatureTick(42.0, '42,0 °C'),
  ];

  final double temperature;
  final Color activeColor;
  final ValueChanged<double> onChanged;

  const _TemperatureInput({
    required this.temperature,
    required this.activeColor,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final inactiveTrackColor = colorScheme.onSurfaceVariant.withValues(
      alpha: 0.22,
    );

    return Column(
      children: [
        SliderTheme(
          data: SliderTheme.of(context).copyWith(
            activeTrackColor: activeColor,
            inactiveTrackColor: inactiveTrackColor,
            thumbColor: activeColor,
            overlayColor: activeColor.withValues(alpha: 0.14),
            valueIndicatorColor: activeColor,
            trackHeight: 5,
          ),
          child: Slider(
            value: temperature,
            min: _minTemperature,
            max: _maxTemperature,
            divisions: 60,
            label: '${temperature.toStringAsFixed(1).replaceAll('.', ',')} °C',
            onChanged: (value) => onChanged((value * 10).round() / 10),
          ),
        ),
        Transform.translate(
          offset: const Offset(0, -10),
          child: SizedBox(
            height: 48,
            child: CustomPaint(
              painter: _TemperatureScalePainter(
                ticks: _ticks,
                tickColor: colorScheme.onSurfaceVariant.withValues(alpha: 0.62),
                textColor: colorScheme.onSurfaceVariant,
              ),
              child: const SizedBox.expand(),
            ),
          ),
        ),
      ],
    );
  }
}

class _TemperatureTick {
  final double value;
  final String label;

  const _TemperatureTick(this.value, this.label);
}

class _TemperatureScalePainter extends CustomPainter {
  final List<_TemperatureTick> ticks;
  final Color tickColor;
  final Color textColor;

  const _TemperatureScalePainter({
    required this.ticks,
    required this.tickColor,
    required this.textColor,
  });

  @override
  void paint(Canvas canvas, Size size) {
    const sliderHorizontalInset = 24.0;
    final trackLeft = sliderHorizontalInset;
    final trackWidth = size.width - sliderHorizontalInset * 2;
    final tickPaint = Paint()
      ..color = tickColor
      ..strokeWidth = 1.5
      ..strokeCap = StrokeCap.round;

    for (var index = 0; index < ticks.length; index++) {
      final tick = ticks[index];
      final x = trackLeft + (index / (ticks.length - 1)) * trackWidth;
      final labelTop = index.isEven ? 17.0 : 31.0;

      canvas.drawLine(Offset(x, 0), Offset(x, 14), tickPaint);
      _drawCenteredLabel(canvas, tick.label, x, labelTop, size.width);
    }
  }

  void _drawCenteredLabel(
    Canvas canvas,
    String label,
    double centerX,
    double y,
    double maxWidth,
  ) {
    final textPainter = TextPainter(
      text: TextSpan(
        text: label,
        style: TextStyle(
          color: textColor,
          fontSize: 9,
          fontWeight: FontWeight.w700,
        ),
      ),
      textDirection: TextDirection.ltr,
    )..layout();

    final left = (centerX - textPainter.width / 2).clamp(
      0.0,
      maxWidth - textPainter.width,
    );
    textPainter.paint(canvas, Offset(left, y));
  }

  @override
  bool shouldRepaint(_TemperatureScalePainter oldDelegate) {
    return oldDelegate.ticks != ticks ||
        oldDelegate.tickColor != tickColor ||
        oldDelegate.textColor != textColor;
  }
}
