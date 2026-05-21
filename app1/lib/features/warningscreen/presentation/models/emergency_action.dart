import 'package:flutter/material.dart';

class EmergencyAction {
  final IconData icon;
  final String text;
  final String? highlightedText;

  const EmergencyAction({
    required this.icon,
    required this.text,
    this.highlightedText,
  });
}
