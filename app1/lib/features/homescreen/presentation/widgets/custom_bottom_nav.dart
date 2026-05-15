import 'package:flutter/material.dart';

class CustomBottomNav extends StatelessWidget {
  const CustomBottomNav({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.fromLTRB(15, 0, 15, 20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(40),
        border: Border.all(color: Colors.teal[100]!),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(40),
        child: BottomNavigationBar(
          elevation: 0,
          backgroundColor: Colors.transparent,
          type: BottomNavigationBarType.fixed,
          selectedItemColor: const Color(0xFF26A69A),
          unselectedItemColor: Colors.teal[200],
          currentIndex: 0,
          items: const [
            BottomNavigationBarItem(icon: Icon(Icons.home_outlined), label: "Startseite"),
            BottomNavigationBarItem(icon: Icon(Icons.calendar_today_outlined), label: "Kalender"),
            BottomNavigationBarItem(icon: Icon(Icons.chat_bubble_outline), label: "Nachrichten"),
            BottomNavigationBarItem(icon: Icon(Icons.settings_outlined), label: "Einstellungen"),
          ],
        ),
      ),
    );
  }
}