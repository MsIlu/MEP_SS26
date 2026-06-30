import 'package:app1/core/widgets/careena_empty_state.dart';
import 'package:flutter/material.dart';

/// Empty state for days without planned medication doses.
class EmptyPlanPill extends StatelessWidget {
  const EmptyPlanPill({super.key});

  @override
  Widget build(BuildContext context) {
    return const CareenaEmptyState(
      icon: Icons.event_busy_outlined,
      title: 'Keine Medikamente geplant',
      message: 'Für diesen Tag sind keine Einnahmen geplant.',
    );
  }
}
