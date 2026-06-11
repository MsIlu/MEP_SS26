import 'package:flutter/material.dart';

class AppointmentEmptyState extends StatelessWidget {
  const AppointmentEmptyState({super.key});

  @override
Widget build(BuildContext context) {
  return Center(
    child: Column(
      mainAxisAlignment: MainAxisAlignment.start,
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        const SizedBox(height: 60),
        const Icon(
          Icons.calendar_month,
          size: 80,
        ),

        const SizedBox(height: 16),

        const Text(
          'Noch keine Termine vorhanden',
          textAlign: TextAlign.center,
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),

        const SizedBox(height: 8),

        Text(
          'Drücke auf das "+" um einen Termin hinzuzufügen',
          textAlign: TextAlign.center,
          style: TextStyle(
            color: Theme.of(context).hintColor,
          ),
        ),
      ],
    ),
  );
}
}