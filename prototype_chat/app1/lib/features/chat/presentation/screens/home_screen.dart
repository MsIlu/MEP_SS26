import 'package:flutter/material.dart';
import '../chat_controller.dart';
import 'package:app1/features/chat/presentation/chat_screen.dart';
import 'package:app1/features/chat/presentation/themes/app_colors.dart';

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

              /// 👋 Moderner Header
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
                    /// Avatar
                    const CircleAvatar(
                      radius: 26,
                      backgroundColor: Colors.white,
                      child: Icon(Icons.person, color: AppColors.primary),
                    ),

                    const SizedBox(width: 12),

                    /// Text
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: const [
                          Text(
                            "Guten Tag 👋",
                            style: TextStyle(
                              fontSize: 16,
                              color: Colors.white70,
                            ),
                          ),
                          SizedBox(height: 4),
                          Text(
                            "Wie kann ich dir helfen?",
                            style: TextStyle(
                              fontSize: 22,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                          ),
                        ],
                      ),
                    ),

                    /// Optional Icon
                    const Icon(Icons.notifications_none, color: Colors.white),
                  ],
                ),
              ),

              /// Fake Search Bar
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
                      "Symptome oder Fragen suchen...",
                      style: TextStyle(color: AppColors.textSecondary),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 25),

              /// Feature Grid
              Expanded(
                child: GridView.count(
                  crossAxisCount: 3,
                  crossAxisSpacing: 10,
                  mainAxisSpacing: 10,
                  childAspectRatio: 0.9,
                  children: [

                    /// Chat (funktioniert)
                    _FeatureTile(
                      icon: Icons.chat_bubble_outline,
                      title: "Chat starten",
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

                    /// Dummy Features
                    _FeatureTile(
                      icon: Icons.assignment,
                      title: "Ersteinschätzung",
                      color: AppColors.accent,
                    ),

                    _FeatureTile(
                      icon: Icons.calendar_today,
                      title: "Terminplanung",
                      color: Colors.orange,
                    ),

                    _FeatureTile(
                      icon: Icons.medical_services,
                      title: "Rezepte",
                      color: Colors.red,
                    ),

                    _FeatureTile(
                      icon: Icons.health_and_safety,
                      title: "Gesundheit",
                      color: Colors.purple,
                    ),

                    _FeatureTile(
                      icon: Icons.local_hospital,
                      title: "Triage",
                      color: Colors.teal,
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),

      /// Bottom Navigation (optisch)
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
            label: "Verlauf",
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person),
            label: "Profil",
          ),
        ],
      ),
    );
  }
}

/// 🔲 Feature Tile Widget
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
    return GestureDetector(
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
    );
  }
}