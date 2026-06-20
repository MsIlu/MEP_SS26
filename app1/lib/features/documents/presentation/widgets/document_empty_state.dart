import 'package:app1/core/themes/app_colors.dart';
import 'package:flutter/material.dart';

class DocumentEmptyState extends StatelessWidget {
  final bool hasActiveFilter;
  final VoidCallback onUpload;

  const DocumentEmptyState({
    super.key,
    required this.hasActiveFilter,
    required this.onUpload,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 320),
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 36),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(
                Icons.folder_open_outlined,
                size: 64,
                color: AppColors.careenaTeal,
              ),
              const SizedBox(height: 16),
              Text(
                hasActiveFilter
                    ? 'Keine passenden Dokumente'
                    : 'Noch keine Dokumente',
                textAlign: TextAlign.center,
                style: Theme.of(
                  context,
                ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800),
              ),
              const SizedBox(height: 8),
              Text(
                hasActiveFilter
                    ? 'Passe deine Suche oder den ausgewählten Filter an.'
                    : 'Lege wichtige Befunde, Laborwerte und weitere Unterlagen zentral ab.',
                textAlign: TextAlign.center,
              ),
              if (!hasActiveFilter) ...[
                const SizedBox(height: 20),
                FilledButton.icon(
                  onPressed: onUpload,
                  icon: const Icon(Icons.upload_file_outlined),
                  label: const Text('Dokument hinzufügen'),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
