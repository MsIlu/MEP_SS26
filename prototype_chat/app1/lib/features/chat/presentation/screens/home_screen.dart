import 'package:flutter/material.dart';
import '../chat_controller.dart';
import 'package:app1/features/chat/presentation/screens/chat_screen.dart';
import 'package:app1/features/chat/presentation/themes/app_colors.dart';

/// Home screen of the application.
///
/// This screen acts as the main entry point and provides:
/// - A welcoming header section
/// - Quick access feature tiles
/// - Navigation into the chat feature
/// - A bottom navigation bar for app-wide sections
class HomeScreen extends StatelessWidget {
  final ChatController controller;

  const HomeScreen({super.key, required this.controller});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,

      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [

              /// Header section with greeting and quick status UI
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [
                      AppColors.primary,
                      Color(0xFF6C63FF),
                    ],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Row(
                  children: [
                    /// User avatar placeholder
                    const CircleAvatar(
                      radius: 26,
                      backgroundColor: Colors.white,
                      child: Icon(Icons.person, color: AppColors.primary),
                    ),

                    const SizedBox(width: 12),

                    /// Greeting text section
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: const [
                          Text(
                            "Good day 👋",
                            style: TextStyle(
                              fontSize: 16,
                              color: Colors.white70,
                            ),
                          ),
                          SizedBox(height: 4),
                          Text(
                            "How can I help you?",
                            style: TextStyle(
                              fontSize: 22,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                          ),
                        ],
                      ),
                    ),

                    /// Notification icon (optional UI element)
                    const Icon(Icons.notifications_none, color: Colors.white),
                  ],
                ),
              ),

              const SizedBox(height: 12),

              /// Search bar (UI placeholder / nonfunctional)
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12),
                height: 50,
                decoration: BoxDecoration(
                  color: AppColors.card,
                  borderRadius: BorderRadius.circular(14),
                ),
                child: Row(
                  children: const [
                    Icon(Icons.search, color: AppColors.textSecondary),
                    SizedBox(width: 10),
                    Text(
                      "Search symptoms or questions...",
                      style: TextStyle(color: AppColors.textSecondary),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 25),

              /// Feature grid providing quick navigation shortcuts
              Expanded(
                child: GridView.count(
                  crossAxisCount: 3,
                  crossAxisSpacing: 10,
                  mainAxisSpacing: 10,
                  childAspectRatio: 0.9,
                  children: [

                    /// Chat feature entry point
                    _FeatureTile(
                      icon: Icons.chat_bubble_outline,
                      title: "Start Chat",
                      color: AppColors.primary,
                      onTap: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (_) =>
                                ChatScreen(controller: controller),
                          ),
                        );
                      },
                    ),

                    /// Placeholder feature tiles (future functionality)
                    _FeatureTile(
                      icon: Icons.assignment,
                      title: "Initial Assessment",
                      color: AppColors.accent,
                    ),

                    _FeatureTile(
                      icon: Icons.calendar_today,
                      title: "Appointments",
                      color: Colors.orange,
                    ),

                    _FeatureTile(
                      icon: Icons.medical_services,
                      title: "Prescriptions",
                      color: Colors.red,
                    ),

                    _FeatureTile(
                      icon: Icons.health_and_safety,
                      title: "Health",
                      color: Colors.purple,
                    ),

                    _FeatureTile(
                      icon: Icons.local_hospital,
                      title: "Test",
                      color: Colors.teal,
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),

      /// Bottom navigation bar for primary app sections
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: 0,
        selectedItemColor: AppColors.primary,
        unselectedItemColor: AppColors.textSecondary,
        backgroundColor: AppColors.card,

        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.home),
            label: "Home",
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.history),
            label: "History",
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person),
            label: "Profile",
          ),
        ],
      ),
    );
  }
}

/// Individual feature tile used in the home screen grid.
///
/// Represents a clickable shortcut to a feature module.
class _FeatureTile extends StatelessWidget {
  final IconData icon;
  final String title;
  final Color color;
  final VoidCallback? onTap;

  const _FeatureTile({
    required this.icon,
    required this.title,
    required this.color,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      cursor: SystemMouseCursors.click,
      child: GestureDetector(
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: AppColors.card,
            borderRadius: BorderRadius.circular(14),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.04),
                blurRadius: 6,
                offset: const Offset(0, 2),
              )
            ],
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              CircleAvatar(
                radius: 18,
                backgroundColor: color.withOpacity(0.1),
                child: Icon(icon, color: color),
              ),
              const SizedBox(height: 8),
              Text(
                title,
                textAlign: TextAlign.center,
                style: const TextStyle(fontWeight: FontWeight.w600),
              ),
            ],
          ),
        ),
      ),
    );
  }
}