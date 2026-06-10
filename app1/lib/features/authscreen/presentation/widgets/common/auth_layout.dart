import 'package:flutter/material.dart';
import '../../../../../core/widgets/responsive_frame.dart';
import 'package:app1/core/themes/app_colors.dart';
import '../../theme/auth_theme.dart';

/// Layout primitives shared by auth screens and form steps.
class AuthPageScaffold extends StatelessWidget {
  final Widget child;
  final double maxWidth;

  const AuthPageScaffold({
    super.key,
    required this.child,
    this.maxWidth = AuthTheme.screenMaxWidth,
  });

  @override
  Widget build(BuildContext context) {
    final isCompact = ResponsiveBreakpoints.isCompact(context);

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      body: SafeArea(
        child: ResponsivePageBody(
          maxWidth: maxWidth,
          scrollable: true,
          padding: EdgeInsets.fromLTRB(
            isCompact ? 16 : 24,
            16,
            isCompact ? 16 : 24,
            24,
          ),
          child: child,
        ),
      ),
    );
  }
}

class AuthIntro extends StatelessWidget {
  final String title;
  final String subtitle;

  const AuthIntro({super.key, required this.title, required this.subtitle});

  @override
  Widget build(BuildContext context) {
    final isCompact = ResponsiveBreakpoints.isCompact(context);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(title, style: AuthTheme.titleStyle(context, isCompact)),
        const SizedBox(height: 8),
        Text(subtitle, style: AuthTheme.bodyStyle(context)),
      ],
    );
  }
}

class AuthTopBar extends StatelessWidget {
  final VoidCallback onBack;
  final bool showBrand;
  final VoidCallback? onToggleTheme;
  final bool isDarkMode;

  const AuthTopBar({
    super.key,
    required this.onBack,
    this.showBrand = true,
    this.onToggleTheme,
    this.isDarkMode = false,
  });

  @override
  Widget build(BuildContext context) {
    final isDarkTheme = Theme.of(context).brightness == Brightness.dark;

    return Row(
      children: [
        IconButton(
          tooltip: 'Zurück',
          style: IconButton.styleFrom(
            backgroundColor: isDarkTheme
                ? AppColors.toolbarButtonBackgroundDark
                : AppColors.toolbarButtonBackground,
            foregroundColor: isDarkTheme
                ? AppColors.toolbarButtonForegroundDark
                : AppColors.toolbarButtonForeground,
            fixedSize: const Size.square(48),
          ),
          onPressed: onBack,
          icon: const Icon(Icons.arrow_back),
        ),
        if (showBrand) ...[
          const SizedBox(width: 10),
          Image.asset('assets/images/careena_logo.png', height: 44),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              'MedBitAid v.1',
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.w800,
                color: AppColors.careenaBrand,
              ),
            ),
          ),
        ] else
          const Spacer(),
        if (onToggleTheme != null)
          IconButton(
            tooltip: isDarkMode
                ? 'Lightmode aktivieren'
                : 'Darkmode aktivieren',
            style: IconButton.styleFrom(
              backgroundColor: isDarkTheme
                  ? AppColors.toolbarButtonBackgroundDark
                  : AppColors.toolbarButtonBackground,
              foregroundColor: isDarkTheme
                  ? AppColors.toolbarButtonForegroundDark
                  : AppColors.toolbarButtonForeground,
              fixedSize: const Size.square(48),
            ),
            icon: Icon(isDarkMode ? Icons.light_mode : Icons.dark_mode),
            onPressed: onToggleTheme,
          ),
      ],
    );
  }
}

class AuthSectionTitle extends StatelessWidget {
  final String text;

  const AuthSectionTitle(this.text, {super.key});

  @override
  Widget build(BuildContext context) {
    return Text(text, style: AuthTheme.sectionTitleStyle(context));
  }
}

class AdaptiveFieldRow extends StatelessWidget {
  final List<Widget> children;
  final double horizontalGap;
  final double verticalGap;

  const AdaptiveFieldRow({
    super.key,
    required this.children,
    this.horizontalGap = 12,
    this.verticalGap = 16,
  });

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        if (constraints.maxWidth < 420) {
          return Column(
            children: [
              for (var index = 0; index < children.length; index++) ...[
                children[index],
                if (index < children.length - 1) SizedBox(height: verticalGap),
              ],
            ],
          );
        }

        return Row(
          children: [
            for (var index = 0; index < children.length; index++) ...[
              Expanded(child: children[index]),
              if (index < children.length - 1) SizedBox(width: horizontalGap),
            ],
          ],
        );
      },
    );
  }
}