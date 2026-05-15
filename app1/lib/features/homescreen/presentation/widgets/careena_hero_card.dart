import 'package:flutter/material.dart';
import 'floating_avatar.dart';

class CareenaHeroCard extends StatelessWidget {
  final VoidCallback onTap;
  const CareenaHeroCard({super.key, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFFB8E4E8),
        borderRadius: BorderRadius.circular(30),
      ),
      child: Row(
        children: [
          const FloatingAvatar(imagePath: 'images/careena_doctor.png'),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text("Ich bin Careena!\nWie kann ich dir helfen?",
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                const SizedBox(height: 11),
                ElevatedButton(
                  onPressed: onTap,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF26A69A),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                  ),
                  child: const Text("Jetzt mit Careena sprechen",
                      style: TextStyle(color: Colors.white, fontSize: 13)),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}