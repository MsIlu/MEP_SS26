import 'package:flutter/material.dart';
import '../chat_controller.dart';
import 'package:app1/features/chat/presentation/chat_screen.dart';

class HomeScreen extends StatelessWidget {
  final ChatController controller;

  const HomeScreen({super.key, required this.controller});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF2F5FA),

      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [

              /// 👋 Header
              const Text(
                "Hallo 👋",
                style: TextStyle(fontSize: 18, color: Colors.grey),
              ),

              const SizedBox(height: 6),

              const Text(
                "Wie kann ich dir helfen?",
                style: TextStyle(
                  fontSize: 26,
                  fontWeight: FontWeight.bold,
                ),
              ),

              const SizedBox(height: 20),

              /// Fake Search Bar
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12),
                height: 50,
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(14),
                ),
                child: Row(
                  children: const [
                    Icon(Icons.search, color: Colors.grey),
                    SizedBox(width: 10),
                    Text(
                      "Symptome oder Fragen suchen...",
                      style: TextStyle(color: Colors.grey),
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
                      color: Colors.blue,
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
                      color: Colors.green,
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
          color: Colors.white,
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