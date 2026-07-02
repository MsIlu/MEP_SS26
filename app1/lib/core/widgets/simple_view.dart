import 'dart:math' as math;

import 'package:app1/core/themes/app_colors.dart';
import 'package:flutter/material.dart';

/// App-wide accessibility context for the simple view.
///
/// Keep this close to MaterialApp so every feature gets larger, calmer UI
/// defaults without each screen needing a direct ThemeController dependency.
class SimpleViewScope extends InheritedWidget {
  final bool enabled;

  const SimpleViewScope({
    super.key,
    required this.enabled,
    required super.child,
  });

  static bool isEnabled(BuildContext context) {
    return context
            .dependOnInheritedWidgetOfExactType<SimpleViewScope>()
            ?.enabled ??
        false;
  }

  @override
  bool updateShouldNotify(SimpleViewScope oldWidget) {
    return enabled != oldWidget.enabled;
  }
}

class SimpleViewAppDefaults extends StatelessWidget {
  final bool enabled;
  final Widget child;

  const SimpleViewAppDefaults({
    super.key,
    required this.enabled,
    required this.child,
  });

  @override
  Widget build(BuildContext context) {
    if (!enabled) {
      return SimpleViewScope(enabled: false, child: child);
    }

    final mediaQuery = MediaQuery.of(context);
    final currentScale = mediaQuery.textScaler.scale(1);
    final scale = math.max(1.18, math.min(currentScale * 1.18, 1.45));

    return SimpleViewScope(
      enabled: true,
      child: MediaQuery(
        data: mediaQuery.copyWith(
          textScaler: TextScaler.linear(scale),
          boldText: true,
        ),
        child: Theme(data: _simpleTheme(Theme.of(context)), child: child),
      ),
    );
  }

  ThemeData _simpleTheme(ThemeData base) {
    final textColor = base.colorScheme.onSurface;
    final mutedTextColor = base.colorScheme.onSurfaceVariant;

    return base.copyWith(
      visualDensity: VisualDensity.comfortable,
      splashFactory: InkRipple.splashFactory,
      listTileTheme: base.listTileTheme.copyWith(
        minTileHeight: 72,
        minLeadingWidth: 48,
        contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
        titleTextStyle: base.textTheme.titleMedium?.copyWith(
          color: textColor,
          fontWeight: FontWeight.w800,
        ),
        subtitleTextStyle: base.textTheme.bodyMedium?.copyWith(
          color: mutedTextColor,
          height: 1.35,
        ),
      ),
      iconButtonTheme: IconButtonThemeData(
        style: IconButton.styleFrom(
          minimumSize: const Size.square(56),
          fixedSize: const Size.square(56),
          iconSize: 30,
        ),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          minimumSize: const Size(64, 58),
          padding: const EdgeInsets.symmetric(horizontal: 22, vertical: 16),
          textStyle: const TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.w800,
          ),
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          minimumSize: const Size(64, 58),
          padding: const EdgeInsets.symmetric(horizontal: 22, vertical: 16),
          textStyle: const TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.w800,
          ),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          minimumSize: const Size(64, 58),
          padding: const EdgeInsets.symmetric(horizontal: 22, vertical: 16),
          textStyle: const TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.w800,
          ),
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          minimumSize: const Size(56, 52),
          padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
          textStyle: const TextStyle(fontWeight: FontWeight.w800),
        ),
      ),
      inputDecorationTheme: base.inputDecorationTheme.copyWith(
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 20,
          vertical: 18,
        ),
      ),
      dividerTheme: base.dividerTheme.copyWith(
        color: AppColors.transparent,
        space: 0,
        thickness: 0,
      ),
    );
  }
}