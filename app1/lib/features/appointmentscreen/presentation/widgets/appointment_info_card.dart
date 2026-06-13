import 'package:flutter/material.dart';
import 'package:app1/core/themes/app_colors.dart';

class AppointmentInfoCard extends StatelessWidget {
  const AppointmentInfoCard({super.key});

  @override
  Widget build(BuildContext context) {
    final isDarkMode =
        Theme.of(context).brightness == Brightness.dark;
    final colorScheme = Theme.of(context).colorScheme;

    return Container(
  padding: const EdgeInsets.all(12),
  decoration: BoxDecoration(
    color: isDarkMode
        ? colorScheme.surface
        : const Color(0xFFE8F6F6),

    borderRadius: BorderRadius.circular(16),

    border: Border.all(
      color: AppColors.careenaTeal,
      width: 1.5,
    ),
  ),
  child: Row(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Icon(
        Icons.tips_and_updates_outlined,
        color: isDarkMode
            ? Colors.white
            : AppColors.careenaTeal,
      ),

      const SizedBox(width: 12),

      Expanded(
        child: Text(
          'Verwalte deine Arzttermine, markiere erledigte Termine und füge neue Termine hinzu.',
          style: TextStyle(
            color: colorScheme.onSurface,
          ),
        ),
      ),
    ],
  ),
);
  }
}
