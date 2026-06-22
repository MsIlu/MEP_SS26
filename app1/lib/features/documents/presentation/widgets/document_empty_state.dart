import 'package:app1/core/themes/app_colors.dart';
import 'package:flutter/material.dart';

class DocumentEmptyState extends StatelessWidget {
  final bool hasActiveFilter;

  const DocumentEmptyState({super.key, required this.hasActiveFilter});

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: Alignment.topCenter,
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 280),
        child: Padding(
          padding: const EdgeInsets.only(top: 48, bottom: 24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                Icons.folder_open_outlined,
                size: 64,
                color: AppColors.careenaTeal.withValues(alpha: 0.9),
              ),
              const SizedBox(height: 16),
              Text(
                hasActiveFilter
                    ? 'Keine passenden Dokumente'
                    : 'Noch keine Dokumente',
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  color: AppColors.careenaTeal,
                  fontWeight: FontWeight.w800,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                hasActiveFilter
                    ? 'Passe deine Suche oder den ausgewählten Filter an.'
                    : 'Lege wichtige Befunde, Laborwerte und weitere Unterlagen zentral ab.',
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: AppColors.careenaTeal.withValues(alpha: 0.75),
                  height: 1.35,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
