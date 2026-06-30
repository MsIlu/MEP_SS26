import 'package:app1/core/themes/app_colors.dart';
import 'package:flutter/material.dart';

/// Checkbox control for marking one planned dose as taken.
class TakenCheckbox extends StatelessWidget {
  final bool value;
  final bool enabled;
  final ValueChanged<bool> onChanged;

  const TakenCheckbox({
    super.key,
    required this.value,
    required this.enabled,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final label = value
        ? 'Medikament als nicht eingenommen markieren'
        : 'Medikament als eingenommen markieren';

    return Semantics(
      button: true,
      checked: value,
      enabled: enabled,
      label: enabled ? label : 'Einnahme erst am Einnahmetag möglich',
      onTap: enabled ? () => onChanged(!value) : null,
      child: ExcludeSemantics(
        child: Tooltip(
          message: enabled
              ? 'Eingenommen markieren'
              : 'Erst am Einnahmetag möglich',
          child: InkWell(
            onTap: enabled ? () => onChanged(!value) : null,
            borderRadius: BorderRadius.circular(12),
            child: Padding(
              padding: const EdgeInsets.only(left: 8),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Checkbox(
                    value: value,
                    activeColor: AppColors.careenaTeal,
                    onChanged: enabled
                        ? (checked) => onChanged(checked ?? false)
                        : null,
                  ),
                  Text(
                    'Eingenommen',
                    style: TextStyle(
                      color: enabled
                          ? colorScheme.onSurfaceVariant
                          : colorScheme.onSurfaceVariant.withValues(
                              alpha: 0.62,
                            ),
                      fontSize: 11,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
