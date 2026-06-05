import 'package:flutter/material.dart';
import '../../../chatscreen/presentation/themes/app_colors.dart';

/// Branding row shown at the top of the onboarding screen.
class OnboardingHeader extends StatelessWidget {
  final VoidCallback onToggleTheme;
  final bool isDarkMode;

  const OnboardingHeader({
    super.key,
    required this.onToggleTheme,
    required this.isDarkMode,
  });

  @override
  Widget build(BuildContext context) {
    final isDarkTheme = Theme.of(context).brightness == Brightness.dark;

    return LayoutBuilder(
      builder: (context, constraints) {
        // The logo and title scale down together so the row remains single-line
        // on narrow mobile screens.
        final isCompact = constraints.maxWidth < 360;
        final logoHeight = isCompact ? 52.0 : 65.0;
        final titleSize = isCompact ? 20.0 : 24.0;

        return Padding(
          padding: EdgeInsets.symmetric(horizontal: isCompact ? 14 : 22),
          child: Row(
            children: [
              Image.asset("assets/images/careena_logo.png", height: logoHeight),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  "MedBitAid v.1",
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(
                    fontSize: titleSize,
                    fontWeight: FontWeight.bold,
                    color: AppColors.careenaBrand,
                  ),
                ),
              ),
              IconButton(
                tooltip: isDarkMode ? 'Lightmode aktivieren' : 'Darkmode aktivieren',
                style: IconButton.styleFrom(
                  backgroundColor: isDarkTheme
                      ? AppColors.toolbarButtonBackgroundDark
                      : AppColors.toolbarButtonBackground,
                  foregroundColor: isDarkTheme
                      ? AppColors.toolbarButtonForegroundDark
                      : AppColors.toolbarButtonForeground,
                ),
                icon: Icon(isDarkMode ? Icons.light_mode : Icons.dark_mode),
                onPressed: onToggleTheme,
              ),
            ],
          ),
        );
      },
    );
  }
}