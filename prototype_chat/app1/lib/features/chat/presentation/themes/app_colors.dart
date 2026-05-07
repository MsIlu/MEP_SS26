import 'package:flutter/material.dart';

/// Centralized definition of all UI colors.
///
/// This class acts as a design system foundation and ensures
/// consistent color usage across the entire application.
class AppColors {

  // =============================
  // Primary Colors (Medical UI)
  // =============================

  /// Main brand color used for primary actions, buttons, and highlights.
  static const Color primary = Color(0xFF4A90E2);

  /// Secondary accent color used for positive states and health-related elements.
  static const Color accent = Color(0xFF2ECC71);


  // =============================
  // Background Colors
  // =============================

  /// Default background color of the application.
  static const Color background = Color(0xFFF2F5FA);

  /// Background color used for cards, tiles, and elevated surfaces.
  static const Color card = Colors.white;


  // =============================
  // Text Colors
  // =============================

  /// Primary text color used for headings and important content.
  static const Color textPrimary = Color(0xFF1F2D3D);

  /// Secondary text color used for hints, labels, and less important content.
  static const Color textSecondary = Colors.grey;


  // =============================
  // Legacy Colors (Backward Compatibility)
  // =============================

  /// Legacy color for the upper app bar background.
  static const Color upperBarColor = Color(0xFF1565C0);

  /// Legacy color for the lower navigation bar background.
  static const Color lowerBarColor = Color(0xFFE0E0E0);
}