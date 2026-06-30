import 'package:app1/core/themes/app_colors.dart';
import 'package:app1/core/widgets/careena_empty_state.dart';
import 'package:flutter/material.dart';

import '../../data/symptom_entry.dart';
import '../utils/symptom_intensity.dart';

/// Shows all symptom entries for the currently selected day.
class SymptomEntryList extends StatelessWidget {
  final bool isLoading;
  final List<SymptomEntry> entries;
  final ValueChanged<SymptomEntry> onDelete;
  final ValueChanged<SymptomEntry>? onEdit;

  const SymptomEntryList({
    super.key,
    required this.isLoading,
    required this.entries,
    required this.onDelete,
    this.onEdit,
  });

  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return Semantics(
        liveRegion: true,
        label: 'Symptomeinträge werden geladen',
        child: const Center(child: CircularProgressIndicator()),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          entries.isEmpty
              ? 'Einträge für diesen Tag'
              : entries.length == 1
              ? '1 Eintrag für diesen Tag'
              : '${entries.length} Einträge für diesen Tag',
          style: TextStyle(
            color: Theme.of(context).colorScheme.onSurface,
            fontSize: 18,
            fontWeight: FontWeight.w800,
          ),
        ),
        const SizedBox(height: 10),
        if (entries.isEmpty)
          const _EmptySymptomState()
        else
          ...entries.map(
            (entry) => Padding(
              padding: const EdgeInsets.only(bottom: 10),
              child: _SymptomEntryTile(
                entry: entry,
                onDelete: onDelete,
                onEdit: onEdit,
              ),
            ),
          ),
      ],
    );
  }
}

class _EmptySymptomState extends StatelessWidget {
  const _EmptySymptomState();

  @override
  Widget build(BuildContext context) {
    return const Semantics(
      liveRegion: true,
      label: 'Noch keine Einträge vorhanden.',
      child: ExcludeSemantics(
        child: CareenaEmptyState(
          icon: Icons.check_circle_outline,
          title: 'Noch keine Einträge vorhanden',
          message: 'Trage deinen ersten Eintrag über das Plus "+" hinzu.',
        ),
      ),
    );
  }
}

class _SymptomEntryTile extends StatelessWidget {
  final SymptomEntry entry;
  final ValueChanged<SymptomEntry> onDelete;
  final ValueChanged<SymptomEntry>? onEdit;

  const _SymptomEntryTile({
    required this.entry,
    required this.onDelete,
    this.onEdit,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    final intensityColor = SymptomIntensity.color(entry.intensity);
    final semanticLabel = _semanticLabel(entry);

    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: colorScheme.surface,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(
          color: isDarkMode
              ? colorScheme.outlineVariant.withValues(alpha: 0.55)
              : AppColors.careenaBorder,
        ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(
            child: Semantics(
              container: true,
              label: semanticLabel,
              child: ExcludeSemantics(
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      width: 46,
                      height: 46,
                      alignment: Alignment.center,
                      decoration: BoxDecoration(
                        color: intensityColor.withValues(alpha: 0.16),
                        borderRadius: BorderRadius.circular(14),
                      ),
                      child: Icon(
                        _iconForEntry(entry),
                        color: intensityColor,
                        size: 25,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Flexible(
                                child: Text(
                                  entry.symptom,
                                  style: TextStyle(
                                    color: colorScheme.onSurface,
                                    fontSize: 16,
                                    fontWeight: FontWeight.w800,
                                  ),
                                ),
                              ),
                              if (entry.source == 'careena') ...[
                                const SizedBox(width: 6),
                                const Tooltip(
                                  message: 'Von Careena empfohlen',
                                  child: Icon(
                                    Icons.auto_awesome,
                                    size: 17,
                                    color: AppColors.careenaTeal,
                                  ),
                                ),
                              ],
                              if (!entry.isSynced || entry.pendingUpdate) ...[
                                const SizedBox(width: 6),
                                Icon(
                                  Icons.cloud_upload_outlined,
                                  size: 17,
                                  color: colorScheme.onSurfaceVariant,
                                ),
                              ],
                            ],
                          ),
                          if (entry.bodyArea.isNotEmpty) ...[
                            const SizedBox(height: 3),
                            Row(
                              children: [
                                const Icon(
                                  Icons.accessibility_new,
                                  size: 14,
                                  color: AppColors.careenaTeal,
                                ),
                                const SizedBox(width: 4),
                                Text(
                                  entry.bodyArea,
                                  style: const TextStyle(
                                    color: AppColors.careenaTeal,
                                    fontSize: 12,
                                    fontWeight: FontWeight.w800,
                                  ),
                                ),
                              ],
                            ),
                          ],
                          const SizedBox(height: 3),
                          Text(
                            'Intensität ${entry.intensity}/10 · ${SymptomIntensity.label(entry.intensity)}',
                            style: TextStyle(
                              color: intensityColor,
                              fontSize: 12,
                              fontWeight: FontWeight.w800,
                            ),
                          ),
                          if (entry.temperatureC != null) ...[
                            const SizedBox(height: 3),
                            Text(
                              'Temperatur ${entry.temperatureC!.toStringAsFixed(1)} °C',
                              style: TextStyle(
                                color: colorScheme.onSurfaceVariant,
                                fontSize: 12,
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                          ],
                          if (entry.note.isNotEmpty) ...[
                            const SizedBox(height: 6),
                            Text(
                              entry.note,
                              style: TextStyle(
                                color: colorScheme.onSurfaceVariant,
                                height: 1.35,
                              ),
                            ),
                          ],
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
          Column(
            children: [
              if (onEdit != null)
                Semantics(
                  button: true,
                  label: 'Eintrag ${entry.symptom} bearbeiten',
                  onTap: () => onEdit!(entry),
                  child: ExcludeSemantics(
                    child: IconButton(
                      tooltip: 'Eintrag ${entry.symptom} bearbeiten',
                      onPressed: () => onEdit!(entry),
                      icon: const Icon(Icons.edit_outlined),
                    ),
                  ),
                ),
              Semantics(
                button: true,
                label: 'Eintrag ${entry.symptom} löschen',
                onTap: () => onDelete(entry),
                child: ExcludeSemantics(
                  child: IconButton(
                    tooltip: 'Eintrag ${entry.symptom} löschen',
                    onPressed: () => onDelete(entry),
                    icon: const Icon(Icons.delete_outline),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  String _semanticLabel(SymptomEntry entry) {
    final parts = <String>[
      'Symptomeintrag: ${entry.symptom}',
      'Intensität ${entry.intensity} von 10',
      SymptomIntensity.label(entry.intensity),
    ];

    if (entry.bodyArea.isNotEmpty) {
      parts.add('Körperbereich: ${entry.bodyArea}');
    }

    if (entry.temperatureC != null) {
      parts.add('Temperatur ${entry.temperatureC!.toStringAsFixed(1)} Grad Celsius');
    }

    if (entry.source == 'careena') {
      parts.add('Von Careena empfohlen');
    }

    if (!entry.isSynced || entry.pendingUpdate) {
      parts.add('Noch nicht synchronisiert');
    }

    if (entry.note.isNotEmpty) {
      parts.add('Notiz: ${entry.note}');
    }

    return parts.join('. ');
  }

  IconData _iconForEntry(SymptomEntry entry) {
    final text = '${entry.symptom} ${entry.bodyArea}'.toLowerCase();

    if (text.contains('kopf')) {
      return Icons.psychology_alt_outlined;
    }

    if (text.contains('müd') || text.contains('schlaf')) {
      return Icons.bedtime_outlined;
    }
    if (text.contains('übel') ||
        text.contains('magen') ||
        text.contains('bauch')) {
      return Icons.sick_outlined;
    }
    if (text.contains('schwindel')) {
      return Icons.blur_circular_outlined;
    }
    if (text.contains('husten') || text.contains('brust')) {
      return Icons.air_outlined;
    }
    if (text.contains('fieber')) {
      return Icons.thermostat_outlined;
    }
    if (text.contains('arm') ||
        text.contains('bein') ||
        text.contains('rücken')) {
      return Icons.accessibility_new;
    }
    if (text.contains('schmerz') ||
        text.contains('weh') ||
        text.contains('stech') ||
        text.contains('brenn') ||
        text.contains('druck') ||
        text.contains('zieh') ||
        text.contains('krampf')) {
      return Icons.healing_outlined;
    }

    return Icons.medical_information_outlined;
  }
}