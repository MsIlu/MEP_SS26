import 'package:flutter/material.dart';

Future<bool> showLeaveChatDialog(BuildContext context) async {
  final shouldLeave = await showDialog<bool>(
    context: context,
    builder: (context) {
      return AlertDialog(
        backgroundColor: const Color(0xFFF7FAF9),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(24),
        ),
        title: const Text(
          'Chat verlassen?',
          style: TextStyle(
            color: Color(0xFF2C5358),
            fontWeight: FontWeight.bold,
            fontSize: 28,
          ),
        ),
        content: const Text(
          'Wenn du fortfährst, gelangst du zurück zum Homescreen. '
              'Der aktuelle Chat wird nicht gespeichert.',
          style: TextStyle(
            color: Color(0xFF2C5358),
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
              foregroundColor: const Color(0xFF2C5358),
              textStyle: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
              ),
            ),
            child: const Text('Abbrechen'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(context).pop(true);
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF2C5358),
              foregroundColor: Colors.white,
              elevation: 0,
              padding: const EdgeInsets.symmetric(
                horizontal: 18,
                vertical: 12,
              ),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(14),
              ),
            ),
            child: const Text(
              'Zum Homescreen',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      );
    },
  );

  return shouldLeave ?? false;
}