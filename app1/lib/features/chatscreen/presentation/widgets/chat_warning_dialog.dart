import 'package:flutter/material.dart';

class ChatWarningDialog extends StatelessWidget {
  const ChatWarningDialog({super.key});

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Wichtiger Hinweis'),
      content: const Text(
        'Diese Antworten dienen ausschließlich der medizinischen Ersteinschätzung '
        'und ersetzen keine ärztliche Diagnose.\n\n'
        'Die Antworten werden durch künstliche Intelligenz (KI) generiert und können '
        'fehlerhafte Informationen enthalten.\n\n'
      ),
      actions: [
        FilledButton(
          onPressed: () {
            Navigator.of(context).pop();
          },
          child: const Text('Verstanden'),
        ),
      ],
    );
  }
}