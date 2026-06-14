import 'package:flutter/material.dart';
import 'package:app1/core/themes/app_colors.dart';

/// Pill-shaped bottom navigation used on the home screen.
class CustomBottomNav extends StatelessWidget {
  final ValueChanged<int>? onTap;
  final bool isSimpleView;

  const CustomBottomNav({super.key, this.onTap, this.isSimpleView = false});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    final navBackgroundColor = isDarkMode
        ? AppColors.darkElevatedSurface
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
                selectedFontSize: isSimpleView ? 16 : 11,
                unselectedFontSize: isSimpleView ? 16 : 11,
                iconSize: isSimpleView ? 32 : 24,
                currentIndex: 0,
                onTap: onTap,
                items: isSimpleView
                    ? const [
                        BottomNavigationBarItem(
                          icon: Icon(Icons.home_outlined),
                          label: "Startseite",
                        ),
                        BottomNavigationBarItem(
                          icon: Icon(Icons.settings_outlined),
                          label: "Einstellungen",
                        ),
                      ]
                    : const [
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
