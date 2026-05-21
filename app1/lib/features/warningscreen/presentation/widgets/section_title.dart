import 'package:flutter/material.dart';

import '../theme/warning_theme.dart';

class SectionTitle extends StatelessWidget {
  final String text;

  const SectionTitle(this.text, {super.key});

  @override
  Widget build(BuildContext context) {
    return Text(
      text,
      style: const TextStyle(
        color: WarningColors.darkText,
        fontWeight: FontWeight.bold,
        fontSize: 15,
      ),
    );
  }
}
