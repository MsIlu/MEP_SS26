import 'package:flutter/material.dart';

import '../../../chatscreen/presentation/themes/app_colors.dart';

/// Search field shown below the home hero card.
class HomeSearchBar extends StatelessWidget {
  /// Whether the field should use the narrow phone spacing.
  final bool isCompact;

  const HomeSearchBar({super.key, required this.isCompact});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.symmetric(
        horizontal: isCompact ? 16 : 20,
        vertical: 15,
      ),
      child: TextField(
        decoration: InputDecoration(
          hintText: 'Suchen...',
          prefixIcon: const Icon(Icons.search),
          filled: true,
          fillColor: AppColors.background,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(30),
            borderSide: BorderSide.none,
          ),
        ),
      ),
    );
  }
}
