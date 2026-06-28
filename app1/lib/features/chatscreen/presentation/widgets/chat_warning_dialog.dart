import 'package:flutter/material.dart';
import 'package:app1/core/themes/app_colors.dart';
import '../../controllers/chat_warning_controller.dart';
import 'package:app1/app/app_dependencies_scope.dart';

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
        'fehlerhafte Informationen enthalten.\n\n',
      ),
      actions: [
        FilledButton(
          style: FilledButton.styleFrom(
            backgroundColor: AppColors.careenaTeal,
            foregroundColor: AppColors.white,
          ),
          onPressed: () {
            ChatWarningController warningController = AppDependenciesScope.of(
              context,
            ).chatWarningController;
            warningController.warningAccepted = true;
            Navigator.of(context).pop(true);
          },
          child: const Text('Verstanden'),
        ),
      ],
    );
  }
}
