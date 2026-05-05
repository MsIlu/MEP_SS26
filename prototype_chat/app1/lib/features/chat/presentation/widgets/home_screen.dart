import 'package:flutter/material.dart';
import '../chat_controller.dart';
import 'package:app1/features/chat/presentation/chat_screen.dart';

class HomeScreen extends StatelessWidget {
  final ChatController controller;

  const HomeScreen({super.key, required this.controller});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F7FB),

      appBar: AppBar(
        title: const Text("MedBitAid"),
        centerTitle: true,
        elevation: 0,
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
      ),

      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [

            const SizedBox(height: 20),

            // 🔵 Hero Card
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(20),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.05),
                    blurRadius: 15,
                    offset: const Offset(0, 5),
                  )
                ],
              ),
              child: Column(
                children: const [
                  Icon(
                    Icons.medical_services_outlined,
                    size: 60,
                    color: Colors.blue,
                  ),
                  SizedBox(height: 10),
                  Text(
                    "Willkommen bei MedBitAid",
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  SizedBox(height: 8),
                  Text(
                    "Dein smarter medizinischer Chat-Assistent für schnelle Antworten und Unterstützung.",
                    textAlign: TextAlign.center,
                    style: TextStyle(color: Colors.grey),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 30),

            // 🔘 Main Button
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blue,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => ChatScreen(controller: controller),
                  ),
                );
              },
              child: const Text(
                "Chat starten",
                style: TextStyle(fontSize: 16),
              ),
            ),

            const SizedBox(height: 20),

            // 🟣 Info Cards
            Expanded(
              child: ListView(
                children: const [
                  _InfoTile(
                    icon: Icons.flash_on,
                    title: "Schnelle Antworten",
                    subtitle: "KI reagiert in Sekunden",
                  ),
                  _InfoTile(
                    icon: Icons.security,
                    title: "Sicher & privat",
                    subtitle: "Keine Speicherung sensibler Daten",
                  ),
                  _InfoTile(
                    icon: Icons.health_and_safety,
                    title: "Medizinischer Fokus",
                    subtitle: "Optimiert für Gesundheitsfragen",
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _InfoTile extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;

  const _InfoTile({
    required this.icon,
    required this.title,
    required this.subtitle,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(15),
      ),
      child: ListTile(
        leading: Icon(icon, color: Colors.blue),
        title: Text(title),
        subtitle: Text(subtitle),
      ),
    );
  }
}