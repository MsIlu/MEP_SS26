import 'package:flutter/material.dart';
import '../../../chatscreen/presentation/themes/app_colors.dart';

class HomeSearchBar extends StatelessWidget {
  const HomeSearchBar({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12),
      height: 50,
      decoration: BoxDecoration(
        color: AppColors.card,
        borderRadius: BorderRadius.circular(14),
      ),
      child: Row(
        children: const [
          Icon(Icons.search, color: AppColors.textSecondary),

          SizedBox(width: 10),

          Text(
            "Suche Symptome oder stelle Fragen...",
            style: TextStyle(color: AppColors.textSecondary),
          ),
        ],
      ),
    );
  }
}