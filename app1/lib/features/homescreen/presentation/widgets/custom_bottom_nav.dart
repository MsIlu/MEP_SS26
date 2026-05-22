import 'package:flutter/material.dart';
import '../../../chatscreen/presentation/themes/app_colors.dart';

/// Pill-shaped bottom navigation used on the home screen.
class CustomBottomNav extends StatelessWidget {
  const CustomBottomNav({super.key});

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      minimum: const EdgeInsets.fromLTRB(15, 0, 15, 12),
      child: Align(
        alignment: Alignment.bottomCenter,
        heightFactor: 1,
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 560),
          child: Container(
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(40),
              border: Border.all(color: AppColors.careenaInfoBorder),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.05),
                  blurRadius: 10,
                  offset: const Offset(0, -2),
                ),
              ],
            ),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(40),
              child: BottomNavigationBar(
                // The navigation is currently static; currentIndex keeps the
                // home item selected until real tab routing is introduced.
                elevation: 0,
                backgroundColor: Colors.transparent,
                type: BottomNavigationBarType.fixed,
                selectedItemColor: AppColors.careenaTeal,
                unselectedItemColor: AppColors.careenaSoftAccent,
                selectedFontSize: 11,
                unselectedFontSize: 11,
                currentIndex: 0,
                items: const [
                  BottomNavigationBarItem(
                    icon: Icon(Icons.home_outlined),
                    label: "Startseite",
                  ),
                  BottomNavigationBarItem(
                    icon: Icon(Icons.calendar_today_outlined),
                    label: "Kalender",
                  ),
                  BottomNavigationBarItem(
                    icon: Icon(Icons.chat_bubble_outline),
                    label: "Nachrichten",
                  ),
                  BottomNavigationBarItem(
                    icon: Icon(Icons.settings_outlined),
                    label: "Einstellungen",
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
