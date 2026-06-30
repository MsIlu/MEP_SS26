import 'package:app1/core/themes/app_colors.dart';
import 'package:flutter/material.dart';

/// Compact day navigation for moving through diary days.
class SymptomDateHeader extends StatelessWidget {
  final String title;
  final VoidCallback onPreviousDay;
  final VoidCallback? onNextDay;
  final VoidCallback? onToday;

  const SymptomDateHeader({
    super.key,
    required this.title,
    required this.onPreviousDay,
    required this.onNextDay,
    required this.onToday,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
      decoration: BoxDecoration(
        color: isDarkMode ? colorScheme.surface : AppColors.white,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(
          color: isDarkMode
              ? colorScheme.outlineVariant.withValues(alpha: 0.55)
              : AppColors.careenaBorder,
        ),
      ),
      child: Row(
        children: [
          Semantics(
            button: true,
            label: 'Vorherigen Tag anzeigen',
            child: ExcludeSemantics(
              child: IconButton(
                tooltip: 'Vorherigen Tag anzeigen',
                onPressed: onPreviousDay,
                icon: const Icon(Icons.chevron_left),
              ),
            ),
          ),
          Expanded(
            child: Column(
              children: [
                Text(
                  title,
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: colorScheme.onSurface,
                    fontSize: 17,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                if (onToday != null) ...[
                  const SizedBox(height: 2),
                  Semantics(
                    button: true,
                    label: 'Heute anzeigen',
                    onTap: onToday,
                    child: ExcludeSemantics(
                      child: TextButton(
                        onPressed: onToday,
                        style: TextButton.styleFrom(
                          minimumSize: Size.zero,
                          padding: const EdgeInsets.symmetric(
                            horizontal: 10,
                            vertical: 3,
                          ),
                          tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                        ),
                        child: const Text('Heute'),
                      ),
                    ),
                  ),
                ],
              ],
            ),
          ),
          Semantics(
            button: true,
            enabled: onNextDay != null,
            label: 'Nächsten Tag anzeigen',
            child: ExcludeSemantics(
              child: IconButton(
                tooltip: 'Nächsten Tag anzeigen',
                onPressed: onNextDay,
                style: IconButton.styleFrom(
                  foregroundColor: onNextDay == null
                      ? colorScheme.onSurfaceVariant.withValues(alpha: 0.45)
                      : null,
                ),
                icon: const Icon(Icons.chevron_right),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
