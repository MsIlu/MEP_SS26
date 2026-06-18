import 'package:app1/core/themes/app_colors.dart';
import 'package:flutter/material.dart';

class RecommendationSummaryCard extends StatelessWidget {
  final String recommendation;

  const RecommendationSummaryCard({super.key, required this.recommendation});

  @override
  Widget build(BuildContext context) {
    final summary = RecommendationSummary.fromText(recommendation);
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    final accent = _accentFor(summary.urgency);
    final backgroundColor = isDarkMode
        ? AppColors.darkElevatedSurface
        : AppColors.careenaNoteBackground;
    final borderColor = accent.withValues(alpha: isDarkMode ? 0.72 : 0.55);

    return Semantics(
      label: 'Handlungs- und Dringlichkeitsempfehlung',
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: backgroundColor,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: borderColor, width: 1.3),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: isDarkMode ? 0.16 : 0.05),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            _RecommendationHeader(accent: accent, urgency: summary.urgency),
            const SizedBox(height: 14),
            Divider(color: borderColor, height: 1),
            const SizedBox(height: 12),
            if (summary.shortSummary.isNotEmpty)
              _RecommendationSection(
                icon: Icons.subject,
                title: 'Kurze Zusammenfassung',
                value: summary.shortSummary,
                accent: accent,
              ),
            if (summary.careLevel.isNotEmpty)
              _RecommendationSection(
                icon: Icons.local_hospital_outlined,
                title: 'Empfohlene Versorgungsebene',
                value: summary.careLevel,
                accent: accent,
              ),
            if (summary.nextStep.isNotEmpty)
              _RecommendationSection(
                icon: Icons.route_outlined,
                title: 'Nächster Schritt',
                value: summary.nextStep,
                accent: accent,
              ),
            if (summary.note.isNotEmpty)
              _RecommendationNote(
                text: summary.note,
                colorScheme: colorScheme,
                isDarkMode: isDarkMode,
              ),
          ],
        ),
      ),
    );
  }

  Color _accentFor(String urgency) {
    final normalized = urgency.toLowerCase();

    if (normalized.contains('hoch') ||
        normalized.contains('sofort') ||
        normalized.contains('notfall')) {
      return AppColors.warningRed;
    }

    if (normalized.contains('mittel') ||
        normalized.contains('zeitnah') ||
        normalized.contains('bald')) {
      return AppColors.symptomIntensityMedium;
    }

    return AppColors.careenaTeal;
  }
}

class _RecommendationHeader extends StatelessWidget {
  final Color accent;
  final String urgency;

  const _RecommendationHeader({required this.accent, required this.urgency});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        CircleAvatar(
          radius: 25,
          backgroundColor: accent.withValues(alpha: 0.18),
          child: Icon(Icons.medical_information_outlined, color: accent),
        ),
        const SizedBox(width: 13),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Handlungsempfehlung',
                style: TextStyle(
                  color: colorScheme.onSurface,
                  fontSize: 18,
                  fontWeight: FontWeight.w900,
                ),
              ),
              const SizedBox(height: 6),
              Wrap(
                spacing: 8,
                runSpacing: 6,
                crossAxisAlignment: WrapCrossAlignment.center,
                children: [
                  Text(
                    'Dringlichkeit',
                    style: TextStyle(
                      color: colorScheme.onSurfaceVariant,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  _UrgencyChip(
                    label: urgency.isEmpty ? 'nicht angegeben' : urgency,
                    color: accent,
                  ),
                ],
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _UrgencyChip extends StatelessWidget {
  final String label;
  final Color color;

  const _UrgencyChip({required this.label, required this.color});

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.16),
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: color.withValues(alpha: 0.45)),
      ),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
        child: Text(
          label,
          style: TextStyle(
            color: color,
            fontSize: 12,
            fontWeight: FontWeight.w900,
          ),
        ),
      ),
    );
  }
}

class _RecommendationSection extends StatelessWidget {
  final IconData icon;
  final String title;
  final String value;
  final Color accent;

  const _RecommendationSection({
    required this.icon,
    required this.title,
    required this.value,
    required this.accent,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Padding(
      padding: const EdgeInsets.only(bottom: 14),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          CircleAvatar(
            radius: 18,
            backgroundColor: accent.withValues(alpha: 0.14),
            child: Icon(icon, size: 18, color: accent),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: TextStyle(
                    color: colorScheme.onSurface,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  value,
                  style: TextStyle(
                    color: colorScheme.onSurfaceVariant,
                    fontSize: 14,
                    height: 1.35,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _RecommendationNote extends StatelessWidget {
  final String text;
  final ColorScheme colorScheme;
  final bool isDarkMode;

  const _RecommendationNote({
    required this.text,
    required this.colorScheme,
    required this.isDarkMode,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(top: 2),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: isDarkMode
            ? colorScheme.surfaceContainerHighest.withValues(alpha: 0.28)
            : Colors.white.withValues(alpha: 0.72),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(
          color: colorScheme.outlineVariant.withValues(alpha: 0.55),
        ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.info_outline, size: 18, color: AppColors.careenaTeal),
          const SizedBox(width: 9),
          Expanded(
            child: Text(
              text,
              style: TextStyle(
                color: colorScheme.onSurfaceVariant,
                fontSize: 12,
                height: 1.35,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class RecommendationSummary {
  final String shortSummary;
  final String urgency;
  final String careLevel;
  final String nextStep;
  final String note;

  const RecommendationSummary({
    required this.shortSummary,
    required this.urgency,
    required this.careLevel,
    required this.nextStep,
    required this.note,
  });

  factory RecommendationSummary.fromText(String text) {
    final sections = <_RecommendationField, List<String>>{};
    _RecommendationField? currentField;

    for (final rawLine in text.split('\n')) {
      final line = rawLine.trim();
      if (line.isEmpty) {
        continue;
      }

      final heading = _parseHeading(line);
      if (heading != null) {
        currentField = heading.field;
        if (heading.value.isNotEmpty) {
          sections.putIfAbsent(currentField, () => []).add(heading.value);
        }
        continue;
      }

      final field = currentField ?? _RecommendationField.shortSummary;
      sections.putIfAbsent(field, () => []).add(line);
    }

    return RecommendationSummary(
      shortSummary: _join(sections[_RecommendationField.shortSummary]),
      urgency: _join(sections[_RecommendationField.urgency]),
      careLevel: _join(sections[_RecommendationField.careLevel]),
      nextStep: _join(sections[_RecommendationField.nextStep]),
      note: _join(sections[_RecommendationField.note]),
    );
  }

  static String _join(List<String>? lines) {
    return lines?.join(' ').trim() ?? '';
  }

  static _ParsedHeading? _parseHeading(String line) {
    final separator = line.indexOf(':');
    if (separator == -1) {
      return null;
    }

    final label = line.substring(0, separator).trim();
    final field = _fieldFor(label);
    if (field == null) {
      return null;
    }

    return _ParsedHeading(
      field: field,
      value: line.substring(separator + 1).trim(),
    );
  }

  static _RecommendationField? _fieldFor(String label) {
    final normalized = _normalize(label);

    if (normalized == 'kurze zusammenfassung' ||
        normalized == 'zusammenfassung') {
      return _RecommendationField.shortSummary;
    }

    if (normalized == 'dringlichkeit') {
      return _RecommendationField.urgency;
    }

    if (normalized == 'empfohlene versorgungsebene' ||
        normalized == 'versorgungsebene') {
      return _RecommendationField.careLevel;
    }

    if (normalized == 'naechster schritt' ||
        normalized == 'nachster schritt' ||
        normalized == 'handlungsempfehlung') {
      return _RecommendationField.nextStep;
    }

    if (normalized == 'hinweis') {
      return _RecommendationField.note;
    }

    return null;
  }

  static String _normalize(String value) {
    return value
        .toLowerCase()
        .replaceAll('ä', 'ae')
        .replaceAll('ö', 'oe')
        .replaceAll('ü', 'ue')
        .replaceAll('ß', 'ss');
  }
}

class _ParsedHeading {
  final _RecommendationField field;
  final String value;

  const _ParsedHeading({required this.field, required this.value});
}

enum _RecommendationField { shortSummary, urgency, careLevel, nextStep, note }
