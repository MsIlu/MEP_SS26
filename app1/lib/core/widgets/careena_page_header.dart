import 'package:app1/core/themes/app_colors.dart';
import 'package:app1/core/widgets/active_profile_header_action.dart';
import 'package:flutter/material.dart';

class CareenaPageHeader extends StatelessWidget implements PreferredSizeWidget {
  final String title;
  final String? compactTitle;
  final bool showBack;
  final VoidCallback? onBack;
  final Widget? leading;
  final Widget? trailing;

  const CareenaPageHeader({
    super.key,
    required this.title,
    this.compactTitle,
    this.showBack = true,
    this.onBack,
    this.leading,
    this.trailing,
  });

  @override
  Size get preferredSize => const Size.fromHeight(64);

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final backgroundColor = isDark
        ? AppColors.headerBackgroundDark
        : AppColors.headerBackgroundLight;
    final trailingWidget = trailing ?? const ActiveProfileHeaderAction();
    final reservesWideTrailing =
        trailing != null || ActiveProfileHeaderAction.hasActiveProfile(context);
    final screenWidth = MediaQuery.sizeOf(context).width;
    final titleSidePadding = reservesWideTrailing
        ? (screenWidth >= 700 ? 228.0 : (screenWidth < 390 ? 112.0 : 156.0))
        : 64.0;

    return AppBar(
      automaticallyImplyLeading: false,
      elevation: 0,
      scrolledUnderElevation: 0,
      backgroundColor: backgroundColor,
      surfaceTintColor: backgroundColor,
      toolbarHeight: preferredSize.height,
      titleSpacing: 12,
      title: Stack(
        alignment: Alignment.center,
        children: [
          Align(
            alignment: Alignment.centerLeft,
            child:
                leading ??
                (showBack
                    ? CareenaHeaderAction(
                        tooltip: 'Zurück',
                        icon: Icons.arrow_back,
                        onPressed: onBack ?? () => Navigator.maybePop(context),
                      )
                    : const SizedBox.square(dimension: 48)),
          ),
          Padding(
            padding: EdgeInsets.symmetric(horizontal: titleSidePadding),
            child: _ResponsiveHeaderTitle(
              title: title,
              compactTitle: compactTitle,
            ),
          ),
          Align(alignment: Alignment.centerRight, child: trailingWidget),
        ],
      ),
    );
  }
}

class _ResponsiveHeaderTitle extends StatelessWidget {
  final String title;
  final String? compactTitle;

  const _ResponsiveHeaderTitle({required this.title, this.compactTitle});

  static const _fontSizes = [20.0, 18.0, 16.0, 14.0];

  @override
  Widget build(BuildContext context) {
    final color = Theme.of(context).colorScheme.onSurface;
    final textDirection = Directionality.of(context);

    return LayoutBuilder(
      builder: (context, constraints) {
        final maxWidth = constraints.maxWidth.isFinite
            ? constraints.maxWidth
            : MediaQuery.sizeOf(context).width;
        final fullTitleFits = _fits(
          title,
          _fontSizes.first,
          maxWidth,
          textDirection,
        );
        final visibleTitle = fullTitleFits ? title : compactTitle ?? title;
        final fontSize = _fontSizes.firstWhere(
          (size) => _fits(visibleTitle, size, maxWidth, textDirection),
          orElse: () => _fontSizes.last,
        );

        return Tooltip(
          message: title,
          child: Semantics(
            header: true,
            label: visibleTitle,
            child: ExcludeSemantics(
              child: Text(
                visibleTitle,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: color,
                  fontSize: fontSize,
                  fontWeight: FontWeight.w800,
                ),
              ),
            ),
          ),
        );
      },
    );
  }

  bool _fits(
    String value,
    double fontSize,
    double maxWidth,
    TextDirection textDirection,
  ) {
    if (maxWidth <= 0) return false;

    final painter = TextPainter(
      text: TextSpan(
        text: value,
        style: TextStyle(fontSize: fontSize, fontWeight: FontWeight.w800),
      ),
      maxLines: 1,
      textDirection: textDirection,
    )..layout(maxWidth: maxWidth);

    return !painter.didExceedMaxLines && painter.width <= maxWidth;
  }
}

class CareenaHeaderAction extends StatelessWidget {
  final String tooltip;
  final IconData icon;
  final VoidCallback? onPressed;

  const CareenaHeaderAction({
    super.key,
    required this.tooltip,
    required this.icon,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return IconButton(
      tooltip: tooltip,
      style: IconButton.styleFrom(
        backgroundColor: isDark
            ? AppColors.toolbarButtonBackgroundDark
            : AppColors.toolbarButtonBackground,
        foregroundColor: isDark
            ? AppColors.toolbarButtonForegroundDark
            : AppColors.toolbarButtonForeground,
        fixedSize: const Size.square(48),
      ),
      onPressed: onPressed,
      icon: Icon(icon),
    );
  }
}
