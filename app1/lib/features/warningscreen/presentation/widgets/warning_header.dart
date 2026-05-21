import 'package:flutter/material.dart';

import '../theme/warning_copy.dart';
import '../theme/warning_layout.dart';
import '../theme/warning_theme.dart';

class WarningHeader extends StatelessWidget {
  const WarningHeader({super.key});

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
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

class _WarningIcon extends StatelessWidget {
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

class _WarningHeaderCopy extends StatelessWidget {
  const _WarningHeaderCopy();

  @override
  Widget build(BuildContext context) {
    return const Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          WarningCopy.headerTitle,
          style: TextStyle(
            color: WarningColors.warningRed,
            fontWeight: FontWeight.bold,
            fontSize: 17,
          ),
        ),
        SizedBox(height: 7),
        Text(
          WarningCopy.headerBody,
          style: TextStyle(
            color: WarningColors.darkText,
            fontSize: 13,
            height: 1.35,
          ),
        ),
      ],
    );
  }
}
