import 'package:flutter/material.dart';
import 'package:app1/core/themes/app_colors.dart';

class AppointmentEmptyState extends StatelessWidget {
  const AppointmentEmptyState({super.key});

  @override
Widget build(BuildContext context) {
  return Center(
    child: Column(
      mainAxisAlignment: MainAxisAlignment.start,
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        const SizedBox(height: 20),
        const Icon(
          Icons.calendar_month,
          color: AppColors.careenaTeal,
          size: 80,
        ),

        const SizedBox(height: 8),

        const Text(
          'Noch keine Termine vorhanden',
          textAlign: TextAlign.center,
          style: TextStyle(
            color: AppColors.careenaTeal,
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),

        const SizedBox(height: 5),

        Text(
          'Drücke auf das "+" um einen Termin hinzuzufügen',
          textAlign: TextAlign.center,
          style: TextStyle(
            color: AppColors.careenaTeal.withOpacity(0.8),
          ),
        ),
      ],
    ),
  );
}
}