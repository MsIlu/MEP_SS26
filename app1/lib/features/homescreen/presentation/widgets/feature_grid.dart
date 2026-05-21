import 'package:flutter/material.dart';
import 'package:app1/features/chatscreen/controllers/chat_controller.dart';
import '../../../chatscreen/presentation/screens/chat_screen.dart';
import '../../../chatscreen/presentation/themes/app_colors.dart';
import '../../../chatscreen/presentation/widgets/feature_tile.dart';

/// Displays a grid of feature tiles on the home screen.
///
/// Each tile represents a specific app feature
/// such as chat, appointments, medication, or health tools.
class FeatureGrid extends StatelessWidget {
  // Controller used for managing chat state
  final ChatController controller;

  const FeatureGrid({super.key, required this.controller});

  @override
  Widget build(BuildContext context) {
    return GridView.count(
      // Number of columns in the grid
      crossAxisCount: 3,
      // Horizontal spacing between tiles
      crossAxisSpacing: 10,
      // Vertical spacing between tiles
      mainAxisSpacing: 10,
      // Width-to-height ratio of each tile
      childAspectRatio: 0.9,

      children: [
        // Chat feature tile
        FeatureTile(
          icon: Icons.chat_bubble_outline,
          title: "Chat starten",
          color: AppColors.primary,
          // Opens the chat screen
          onTap: () {
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => ChatScreen(controller: controller),
              ),
            );
          },
        ),

        // Initial assessment feature
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
