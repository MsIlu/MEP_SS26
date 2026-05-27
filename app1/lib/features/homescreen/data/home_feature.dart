import 'package:flutter/material.dart';

/// Data model for one actionable item on the home screen.
class HomeFeature {
  /// Icon shown at the start of the feature row.
  final IconData icon;

  /// User-facing label for the feature.
  final String title;

  /// Background color used behind the icon.
  final Color backgroundColor;

  /// Callback executed when the user taps the feature.
  final VoidCallback onTap;

  const HomeFeature({
    required this.icon,
    required this.title,
    required this.backgroundColor,
    required this.onTap,
  });
}
