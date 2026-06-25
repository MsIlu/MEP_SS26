import 'package:flutter/material.dart';

/// Centered title used at the top of the medication feature page.
class MedicationPageTitle extends StatelessWidget {
  final String text;

  const MedicationPageTitle({super.key, required this.text});

  @override
  Widget build(BuildContext context) {
    return Text(
      text,
      textAlign: TextAlign.center,
      style: TextStyle(
        color: Theme.of(context).colorScheme.onSurface,
        fontSize: 28,
        fontWeight: FontWeight.w800,
      ),
    );
  }
}