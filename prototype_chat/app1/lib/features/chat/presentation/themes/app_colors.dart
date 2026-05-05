import 'package:flutter/material.dart';

/// Central class for all UI color definitions.
///
/// This class defines a consistent design system
/// for the entire application.
class AppColors {

  // =============================
  // Primary Colors (Medical UI)
  // =============================

  /// Main brand color (used for buttons, highlights)
  static const Color primary = Color(0xFF4A90E2);

  /// Secondary accent color (health-related UI elements)
  static const Color accent = Color(0xFF2ECC71);


  // =============================
  // Background Colors
  // =============================

  /// Main app background
  static const Color background = Color(0xFFF2F5FA);

  /// Card / tile background
  static const Color card = Colors.white;


  // =============================
  // Text Colors
  // =============================

  /// Primary text (headings)
  static const Color textPrimary = Color(0xFF1F2D3D);

  /// Secondary text (descriptions, hints)
  static const Color textSecondary = Colors.grey;


  // =============================
  // Legacy Colors (keep for compatibility)
  // =============================

  /// Background color of the top app bar (legacy)
  static const Color upperBarColor = Color(0xFF1565C0);

  /// Background color of the bottom bar (legacy)
  static const Color lowerBarColor = Color(0xFFE0E0E0);
}