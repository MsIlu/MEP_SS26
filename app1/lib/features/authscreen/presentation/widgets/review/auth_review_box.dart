import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../../../../chatscreen/presentation/themes/app_colors.dart';
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
    return DecoratedBox(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(AuthTheme.fieldRadius),
        border: Border.all(color: AppColors.careenaBorder),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            _ReviewHeader(title: title, onEdit: onEdit),
            const Divider(height: 22, color: AppColors.careenaBorder),
            for (var index = 0; index < items.length; index++) ...[
              _ReviewRow(item: items[index]),
              if (index < items.length - 1)
                const Divider(height: 22, color: AppColors.careenaBorder),
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
          icon: const Icon(Icons.edit_outlined, color: AppColors.careenaTitle),
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
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          width: 148,
          child: Text(
            item.label,
            style: GoogleFonts.nunito(
              fontWeight: FontWeight.w800,
              color: AppColors.careenaTitle,
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Text(
            item.value,
            style: GoogleFonts.nunito(color: AppColors.careenaBody),
          ),
        ),
      ],
    );
  }
}