import 'package:flutter/material.dart';

/// Centers page content and caps it at a readable width on larger screens.
class ResponsiveFrame extends StatelessWidget {
  final Widget child;
  final double maxWidth;
  final EdgeInsetsGeometry padding;

  const ResponsiveFrame({
    super.key,
    required this.child,
    this.maxWidth = 560,
    this.padding = EdgeInsets.zero,
  });

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: Alignment.topCenter,
      child: ConstrainedBox(
        constraints: BoxConstraints(maxWidth: maxWidth),
        child: Padding(padding: padding, child: child),
      ),
    );
  }
}

/// Adds responsive width constraints to pages that need vertical scrolling.
class ResponsiveScrollableFrame extends StatelessWidget {
  final Widget child;
  final double maxWidth;
  final EdgeInsetsGeometry padding;

  const ResponsiveScrollableFrame({
    super.key,
    required this.child,
    this.maxWidth = 560,
    this.padding = EdgeInsets.zero,
  });

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        return SingleChildScrollView(
          child: ConstrainedBox(
            constraints: BoxConstraints(minHeight: constraints.maxHeight),
            child: ResponsiveFrame(
              maxWidth: maxWidth,
              padding: padding,
              child: child,
            ),
          ),
        );
      },
    );
  }
}

/// Shared page wrapper for new screens.
///
/// Use this around the main body content so phone, tablet, and desktop layouts
/// inherit the same width and scroll behavior by default.
class ResponsivePageBody extends StatelessWidget {
  final Widget child;
  final double maxWidth;
  final bool scrollable;
  final EdgeInsetsGeometry padding;

  const ResponsivePageBody({
    super.key,
    required this.child,
    this.maxWidth = 720,
    this.scrollable = false,
    this.padding = EdgeInsets.zero,
  });

  @override
  Widget build(BuildContext context) {
    // Keeps visible page text selectable without touching every Text widget.
    final selectableChild = SelectionArea(child: child);

    if (scrollable) {
      return ResponsiveScrollableFrame(
        maxWidth: maxWidth,
        padding: padding,
        child: selectableChild,
      );
    }

    return LayoutBuilder(
      builder: (context, constraints) {
        return ResponsiveFrame(
          maxWidth: maxWidth,
          padding: padding,
          child: SizedBox(
            width: double.infinity,
            height: constraints.maxHeight,
            child: selectableChild,
          ),
        );
      },
    );
  }
}

/// App-wide layout breakpoints.
class ResponsiveBreakpoints {
  static bool isCompact(BuildContext context) {
    return MediaQuery.sizeOf(context).width < 360;
  }

  static bool isTablet(BuildContext context) {
    return MediaQuery.sizeOf(context).width >= 700;
  }
}
