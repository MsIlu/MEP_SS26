import 'package:flutter/material.dart';
import 'package:app1/features/chat/controllers/chat_controller.dart';
import '../screens/chat_screen.dart';
import '../themes/app_colors.dart';

import 'feature_tile.dart';

class FeatureGrid extends StatelessWidget {
  final ChatController controller;

  const FeatureGrid({
    super.key,
    required this.controller,
  });

  @override
  Widget build(BuildContext context) {
    return GridView.count(
      crossAxisCount: 3,
      crossAxisSpacing: 10,
      mainAxisSpacing: 10,
      childAspectRatio: 0.9,
      children: [
        FeatureTile(
          icon: Icons.chat_bubble_outline,
          title: "Chat starten",
          color: AppColors.primary,
          onTap: () {
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => ChatScreen(
                  controller: controller,
                ),
              ),
            );
          },
        ),

        FeatureTile(
          icon: Icons.assignment,
          title: "Ersteinschätzung",
          color: AppColors.accent,
        ),

        FeatureTile(
          icon: Icons.calendar_today,
          title: "Termine",
          color: Colors.orange,
        ),

        FeatureTile(
          icon: Icons.medical_services,
          title: "Medikamente",
          color: Colors.red,
        ),

        FeatureTile(
          icon: Icons.health_and_safety,
          title: "Gesundheit",
          color: Colors.purple,
        ),

        FeatureTile(
          icon: Icons.local_hospital,
          title: "Test",
          color: Colors.teal,
        ),
      ],
    );
  }
}