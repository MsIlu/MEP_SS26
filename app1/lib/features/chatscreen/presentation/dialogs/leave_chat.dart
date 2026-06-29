import 'package:flutter/material.dart';
import 'package:app1/core/themes/app_colors.dart';

Future<bool> showLeaveChatDialog(
  BuildContext context, {
  String message =
      'Wenn du fortfährst, gelangst du zurück zur Startseite. '
      'Der aktuelle Chat wird nicht gespeichert.',
  String confirmLabel = 'Zur Startseite',
}) async {
  final colorScheme = Theme.of(context).colorScheme;
  final isDarkMode = Theme.of(context).brightness == Brightness.dark;

  final shouldLeave = await showDialog<bool>(
    context: context,
    builder: (context) {
      return AlertDialog(
        backgroundColor: isDarkMode ? colorScheme.surface : AppColors.white,
        surfaceTintColor: AppColors.transparent,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(24),
          side: BorderSide(
            color: isDarkMode
                ? AppColors.transparent
                : AppColors.careenaInfoBorder,
            width: 1,
          ),
        ),
        title: Text(
          'Chat verlassen?',
          style: TextStyle(
            color: isDarkMode ? colorScheme.onSurface : AppColors.careenaTitle,
            fontWeight: FontWeight.bold,
            fontSize: 28,
          ),
        ),
        content: Text(
          message,
          style: TextStyle(
            color: isDarkMode ? colorScheme.onSurface : AppColors.careenaBody,
            fontSize: 16,
            height: 1.4,
          ),
        ),
        actionsPadding: const EdgeInsets.fromLTRB(20, 0, 20, 20),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.of(context).pop(false);
            },
            style: TextButton.styleFrom(
              foregroundColor: isDarkMode
                  ? colorScheme.onSurface
                  : AppColors.careenaDark,
              textStyle: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w700,
              ),
            ),
            child: const Text('Abbrechen'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(context).pop(true);
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: isDarkMode
                  ? AppColors.toolbarButtonBackgroundDark
                  : AppColors.careenaBrand,
              foregroundColor: isDarkMode
                  ? AppColors.toolbarButtonForegroundDark
                  : AppColors.toolbarButtonForeground,
              elevation: 0,
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
            ),
            child: Text(
              confirmLabel,
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
            ),
          ),
        ],
      );
    },
  );

  return shouldLeave ?? false;
}
