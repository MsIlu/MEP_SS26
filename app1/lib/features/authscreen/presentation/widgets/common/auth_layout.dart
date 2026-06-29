import 'package:flutter/material.dart';
import '../../../../../core/widgets/responsive_frame.dart';
import '../../theme/auth_theme.dart';

/// Layout primitives shared by auth screens and form steps.
class AuthPageScaffold extends StatelessWidget {
  final Widget child;
  final PreferredSizeWidget? fixedHeader;
  final double maxWidth;

  const AuthPageScaffold({
    super.key,
    required this.child,
    this.fixedHeader,
    this.maxWidth = AuthTheme.screenMaxWidth,
  });

  @override
  Widget build(BuildContext context) {
    final isCompact = ResponsiveBreakpoints.isCompact(context);

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      body: SafeArea(
        child: Column(
          children: [
            if (fixedHeader != null)
              SizedBox(
                height: fixedHeader!.preferredSize.height,
                child: fixedHeader,
              ),
            Expanded(
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
          ],
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
