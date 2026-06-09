import 'package:app1/core/themes/app_colors.dart';
import 'package:flutter/material.dart';

import '../../data/symptom_entry.dart';
import '../utils/symptom_intensity.dart';

/// Shows the most relevant daily signal instead of repeating raw counts.
class SymptomSummaryCard extends StatelessWidget {
  final List<SymptomEntry> entries;

  const SymptomSummaryCard({super.key, required this.entries});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    final strongestEntry = _strongestEntry;
    final intensityColor = strongestEntry == null
        ? AppColors.careenaTeal
        : SymptomIntensity.color(strongestEntry.intensity);
    final copy = _summaryCopy(strongestEntry);

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: isDarkMode ? AppColors.darkMutedSurface : AppColors.careenaBrand,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 46,
            height: 46,
            alignment: Alignment.center,
            decoration: BoxDecoration(
              color: intensityColor.withValues(alpha: 0.2),
              borderRadius: BorderRadius.circular(15),
              border: Border.all(
                color: intensityColor.withValues(alpha: 0.9),
                width: 2,
              ),
            ),
            child: Icon(copy.icon, color: Colors.white, size: 25),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  copy.eyebrow,
                  style: const TextStyle(
                    color: Colors.white70,
                    fontSize: 12,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  copy.title,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 17,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                const SizedBox(height: 5),
                Text(
                  copy.body,
                  style: TextStyle(
                    color: colorScheme.brightness == Brightness.dark
                        ? Colors.white.withValues(alpha: 0.78)
                        : Colors.white.withValues(alpha: 0.84),
                    height: 1.35,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ),
          if (strongestEntry != null) ...[
            const SizedBox(width: 10),
            _IntensityBadge(
              intensity: strongestEntry.intensity,
              color: intensityColor,
            ),
          ],
        ],
      ),
    );
  }

  SymptomEntry? get _strongestEntry {
    if (entries.isEmpty) {
      return null;
    }

    return entries.reduce((current, next) {
      if (next.intensity > current.intensity) {
        return next;
      }
      if (next.intensity == current.intensity &&
          next.createdAt.isAfter(current.createdAt)) {
        return next;
      }
      return current;
    });
  }

  _DailySummaryCopy _summaryCopy(SymptomEntry? strongestEntry) {
    if (strongestEntry == null) {
      return const _DailySummaryCopy(
        eyebrow: 'Heute im Blick',
        title: 'Noch nichts eingetragen',
        body: 'Trage ein Symptom ein, sobald du eine Veränderung bemerkst.',
        icon: Icons.add_task_outlined,
      );
    }

    final area = strongestEntry.bodyArea.isEmpty
        ? ''
        : ' · ${strongestEntry.bodyArea}';
    final symptomLabel = '${strongestEntry.symptom}$area';

    if (strongestEntry.intensity >= 8) {
      return _DailySummaryCopy(
        eyebrow: 'Stärkstes Symptom',
        title: symptomLabel,
        body:
            'Sehr stark eingestuft. Beobachte den Verlauf eng und kläre neue, ungewohnte oder zunehmende Beschwerden medizinisch ab.',
        icon: Icons.priority_high,
      );
    }

    if (strongestEntry.intensity >= 5) {
      return _DailySummaryCopy(
        eyebrow: 'Stärkstes Symptom',
        title: symptomLabel,
        body:
            'Mittel eingestuft. Ergänze Auslöser, Verlauf oder Situation in der Notiz.',
        icon: Icons.edit_note,
      );
    }

    return _DailySummaryCopy(
      eyebrow: 'Stärkstes Symptom',
      title: symptomLabel,
      body:
          'Leicht eingestuft. Wenn es sich verändert, kannst du später einen neuen Eintrag ergänzen.',
      icon: Icons.check_circle_outline,
    );
  }
}

class _IntensityBadge extends StatelessWidget {
  final int intensity;
  final Color color;

  const _IntensityBadge({required this.intensity, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 54,
      height: 44,
      alignment: Alignment.center,
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.14),
        borderRadius: BorderRadius.circular(14),
      ),
      child: Text(
        '$intensity/10',
        style: TextStyle(
          color: color,
          fontSize: 15,
          fontWeight: FontWeight.w900,
        ),
      ),
    );
  }
}

class _DailySummaryCopy {
  final String eyebrow;
  final String title;
  final String body;
  final IconData icon;

  const _DailySummaryCopy({
    required this.eyebrow,
    required this.title,
    required this.body,
    required this.icon,
  });
}