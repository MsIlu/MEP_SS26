import 'package:flutter/material.dart';

class HomeFeature {
  final IconData icon;
  final String title;
  final Color backgroundColor;
  final VoidCallback onTap;

  const HomeFeature({
    required this.icon,
    required this.title,
    required this.backgroundColor,
    required this.onTap,
  });
}
