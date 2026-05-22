import 'package:flutter/material.dart';
import '../../../chatscreen/presentation/themes/app_colors.dart';

/// Single tappable row in the home feature list.
class FunctionMenuTile extends StatelessWidget {
  /// Leading icon that represents the feature.
  final IconData icon;

  /// Feature label shown in the row.
  final String title;

  /// Background color behind the leading icon.
  final Color bgColor;

  /// Action executed when the tile is selected.
  final VoidCallback onTap;

  const FunctionMenuTile({
    super.key,
    required this.icon,
    required this.title,
    required this.bgColor,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: EdgeInsets.zero,
      decoration: BoxDecoration(
        border: Border.all(color: Colors.grey[200]!),
        borderRadius: BorderRadius.circular(20),
      ),
      child: ListTile(
        onTap: onTap,
        contentPadding: const EdgeInsets.symmetric(horizontal: 15, vertical: 5),
        minVerticalPadding: 12,
        leading: Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: bgColor,
            borderRadius: BorderRadius.circular(12),
          ),
          child: Icon(icon, color: AppColors.careenaDark),
        ),
        title: Text(
          title,
          maxLines: 2,
          overflow: TextOverflow.ellipsis,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            color: AppColors.careenaDark,
          ),
        ),
        trailing: const Icon(Icons.chevron_right, color: AppColors.careenaTeal),
      ),
    );
  }
}