import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../../../../../core/widgets/responsive_frame.dart';
import '../../../../chatscreen/presentation/themes/app_colors.dart';
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
      backgroundColor: AppColors.careenaBackground,
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
        Text(title, style: AuthTheme.titleStyle(isCompact)),
        const SizedBox(height: 8),
        Text(subtitle, style: AuthTheme.bodyStyle()),
      ],
    );
  }
}

class AuthTopBar extends StatelessWidget {
  final VoidCallback onBack;
  final bool showBrand;

  const AuthTopBar({super.key, required this.onBack, this.showBrand = true});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        IconButton.filledTonal(
          tooltip: 'Zurück',
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
              style: GoogleFonts.nunito(
                fontSize: 20,
                fontWeight: FontWeight.w800,
                color: AppColors.careenaBrand,
              ),
            ),
          ),
        ] else
          const Spacer(),
      ],
    );
  }
}

class AuthSectionTitle extends StatelessWidget {
  final String text;

  const AuthSectionTitle(this.text, {super.key});

  @override
  Widget build(BuildContext context) {
    return Text(text, style: AuthTheme.sectionTitleStyle());
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