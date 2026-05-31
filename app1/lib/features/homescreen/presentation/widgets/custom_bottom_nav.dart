import 'package:flutter/material.dart';
import '../../../chatscreen/presentation/themes/app_colors.dart';

/// Pill-shaped bottom navigation used on the home screen.
class CustomBottomNav extends StatelessWidget {
  const CustomBottomNav({super.key});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    final navBackgroundColor = isDarkMode
        ? const Color(0xFF222A35)
        : Colors.white;

    final borderColor = isDarkMode
        ? colorScheme.outlineVariant.withValues(alpha: 0.45)
        : AppColors.careenaInfoBorder;

    final selectedColor = isDarkMode
        ? AppColors.toolbarButtonBackgroundDark
        : AppColors.careenaTeal;

    final unselectedColor = isDarkMode
        ? colorScheme.onSurfaceVariant
        : AppColors.careenaSoftAccent;

    final shadowColor = isDarkMode
        ? Colors.black.withValues(alpha: 0.18)
        : Colors.black.withValues(alpha: 0.05);

    return SafeArea(
      minimum: const EdgeInsets.fromLTRB(15, 0, 15, 12),
      child: Align(
        alignment: Alignment.bottomCenter,
        heightFactor: 1,
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 560),
          child: Container(
            decoration: BoxDecoration(
              color: navBackgroundColor,
              borderRadius: BorderRadius.circular(40),
              border: Border.all(color: borderColor),
              boxShadow: [
                BoxShadow(
                  color: shadowColor,
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
                selectedItemColor: selectedColor,
                unselectedItemColor: unselectedColor,
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
