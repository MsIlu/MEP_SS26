import 'package:flutter/material.dart';
import 'package:app1/core/themes/app_colors.dart';

class AppointmentEmptyState extends StatelessWidget {
  const AppointmentEmptyState({super.key});

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        return SingleChildScrollView(
          child: ConstrainedBox(
            constraints: BoxConstraints(minHeight: constraints.maxHeight),
            child: Center(
              child: Transform.translate(
                offset: const Offset(0, -24),
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 280),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        Icons.calendar_month_outlined,
                        color: AppColors.careenaTeal.withValues(alpha: 0.9),
                        size: 64,
                      ),
                      const SizedBox(height: 16),
                      const Text(
                        'Noch keine Termine vorhanden',
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          color: AppColors.careenaTeal,
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Füge deinen ersten Termin über das Plus "+" hinzu.',
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
            ),
          ),
        );
      },
    );
  }
}
