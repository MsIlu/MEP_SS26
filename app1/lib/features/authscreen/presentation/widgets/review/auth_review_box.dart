import 'package:flutter/material.dart';
import 'package:app1/core/themes/app_colors.dart';
import '../../models/auth_review_item.dart';
import '../../theme/auth_theme.dart';

/// Displays the user's collected registration data before account creation.
class AuthReviewBox extends StatelessWidget {
  final String title;
  final List<AuthReviewItem> items;
  final VoidCallback onEdit;

  const AuthReviewBox({
    super.key,
    required this.title,
    required this.items,
    required this.onEdit,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    final boxColor = isDarkMode ? colorScheme.surface : Colors.white;
    final borderColor = isDarkMode
        ? colorScheme.outlineVariant
        : AppColors.careenaBorder;

    return DecoratedBox(
      decoration: BoxDecoration(
        color: boxColor,
        borderRadius: BorderRadius.circular(AuthTheme.fieldRadius),
        border: Border.all(color: borderColor),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            _ReviewHeader(title: title, onEdit: onEdit),
            Divider(height: 22, color: borderColor),
            for (var index = 0; index < items.length; index++) ...[
              _ReviewRow(item: items[index]),
              if (index < items.length - 1)
                Divider(height: 22, color: borderColor),
            ],
          ],
        ),
      ),
    );
  }
}

class _ReviewHeader extends StatelessWidget {
  final String title;
  final VoidCallback onEdit;

  const _ReviewHeader({required this.title, required this.onEdit});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    final iconColor = isDarkMode
        ? colorScheme.onSurfaceVariant
        : AppColors.careenaTitle;

    return Row(
      children: [
        Expanded(
          child: Text(
            title,
            style: AuthTheme.sectionTitleStyle(context).copyWith(fontSize: 16),
          ),
        ),
        IconButton(
          tooltip: '$title bearbeiten',
          onPressed: onEdit,
          icon: Icon(Icons.edit_outlined, color: iconColor),
        ),
      ],
    );
  }
}

class _ReviewRow extends StatelessWidget {
  final AuthReviewItem item;

  const _ReviewRow({required this.item});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    final labelColor = isDarkMode
        ? colorScheme.onSurface
        : AppColors.careenaTitle;

    final valueColor = isDarkMode
        ? colorScheme.onSurfaceVariant
        : AppColors.careenaBody;

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          width: 148,
          child: Text(
            item.label,
            style: TextStyle(
              fontWeight: FontWeight.w800,
              color: labelColor,
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Text(
            item.value,
            style: TextStyle(color: valueColor),
          ),
        ),
      ],
    );
  }
}