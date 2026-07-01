import 'package:app1/core/widgets/careena_empty_state.dart';
import 'package:flutter/material.dart';

class AppointmentEmptyState extends StatelessWidget {
  const AppointmentEmptyState({super.key});

  @override
  Widget build(BuildContext context) {
    return const CareenaEmptyState(
      icon: Icons.calendar_month_outlined,
      title: 'Noch keine Termine vorhanden',
      message: 'Füge deinen ersten Termin über das Plus "+" hinzu.',
    );
  }
}
