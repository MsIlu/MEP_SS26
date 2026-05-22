import 'package:flutter/material.dart';

/// One recommended emergency action displayed on the warning screen.
class EmergencyAction {
  /// Icon that visually represents the action.
  final IconData icon;

  /// Full action text.
  final String text;

  /// Optional substring emphasized inside [text].
  final String? highlightedText;

  const EmergencyAction({
    required this.icon,
    required this.text,
    this.highlightedText,
  });
}
