import 'package:flutter/material.dart';

import '../theme/warning_copy.dart';
import '../theme/warning_layout.dart';
import '../theme/warning_theme.dart';

/// Top section of the warning card with icon, title, and urgent explanation.
class WarningHeader extends StatelessWidget {
  const WarningHeader({super.key});

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        // The icon and copy stack vertically on narrow cards so the warning
        // title keeps enough readable width.
        final isCompact = constraints.maxWidth < WarningLayout.compactWidth;
        final icon = _WarningIcon(isCompact: isCompact);
        final copy = const _WarningHeaderCopy();

        if (isCompact) {
          return Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [icon, const SizedBox(height: 12), copy],
          );
        }

        return Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            icon,
            const SizedBox(width: 14),
            Expanded(child: copy),
          ],
        );
      },
    );
  }
}

/// Circular warning icon sized for compact and regular card layouts.
class _WarningIcon extends StatelessWidget {
  /// Whether the parent header is using its compact layout.
  final bool isCompact;

  const _WarningIcon({required this.isCompact});

  @override
  Widget build(BuildContext context) {
    return CircleAvatar(
      radius: isCompact ? 24 : 28,
      backgroundColor: WarningColors.warningIconBackground,
      child: Icon(
        Icons.warning_amber_rounded,
        color: WarningColors.warningRed,
        size: isCompact ? 28 : 32,
      ),
    );
  }
}

/// Warning headline and explanatory body copy.
class _WarningHeaderCopy extends StatelessWidget {
  const _WarningHeaderCopy();

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    final bodyColor = isDarkMode
        ? colorScheme.onSurfaceVariant
        : WarningColors.darkText;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          WarningCopy.headerTitle,
          style: TextStyle(
            color: WarningColors.warningRed,
            fontWeight: FontWeight.bold,
            fontSize: 17,
          ),
        ),
        const SizedBox(height: 7),
        Text(
          WarningCopy.headerBody,
          style: TextStyle(
            color: bodyColor,
            fontSize: 13,
            height: 1.35,
          ),
        ),
      ],
    );
  }
}
