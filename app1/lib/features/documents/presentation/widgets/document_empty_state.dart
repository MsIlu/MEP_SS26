import 'package:app1/core/widgets/careena_empty_state.dart';
import 'package:flutter/material.dart';

class DocumentEmptyState extends StatelessWidget {
  final bool hasActiveFilter;

  const DocumentEmptyState({super.key, required this.hasActiveFilter});

  @override
  Widget build(BuildContext context) {
    return CareenaEmptyState(
      icon: Icons.folder_open_outlined,
      title: hasActiveFilter
          ? 'Keine passenden Dokumente'
          : 'Noch keine Dokumente vorhanden',
      message: hasActiveFilter
          ? 'Passe deine Suche oder den ausgewählten Filter an.'
          : 'Lege wichtige Befunde, Laborwerte und weitere Unterlagen zentral ab.',
      padding: const EdgeInsets.fromLTRB(0, 24, 0, 48),
    );
  }
}
