import 'package:app1/core/themes/app_colors.dart';
import 'package:flutter/material.dart';

class RenameDocumentDialog extends StatefulWidget {
  final String initialName;

  const RenameDocumentDialog({super.key, required this.initialName});

  @override
  State<RenameDocumentDialog> createState() => _RenameDocumentDialogState();
}

class _RenameDocumentDialogState extends State<RenameDocumentDialog> {
  late final TextEditingController _nameController;

  @override
  void initState() {
    super.initState();
    _nameController = TextEditingController(text: widget.initialName);
  }

  @override
  void dispose() {
    _nameController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      icon: const Icon(
        Icons.edit_outlined,
        color: AppColors.careenaTeal,
        size: 36,
      ),
      title: const Text(
        'Dokument umbenennen',
        style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
      ),
      content: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 420),
        child: TextField(
          controller: _nameController,
          autofocus: true,
          cursorColor: AppColors.careenaTeal,
          maxLength: 100,
          decoration: InputDecoration(
            labelText: 'Dokumentname',
            floatingLabelStyle: const TextStyle(
              color: AppColors.careenaTeal,
              fontWeight: FontWeight.w600,
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(14),
              borderSide: const BorderSide(
                color: AppColors.careenaTeal,
                width: 2,
              ),
            ),
          ),
          onChanged: (_) => setState(() {}),
          onSubmitted: (_) => _save(),
        ),
      ),
      actions: [
        TextButton(
          style: TextButton.styleFrom(foregroundColor: AppColors.careenaTeal),
          onPressed: () => Navigator.pop(context),
          child: const Text('Abbrechen'),
        ),
        FilledButton(
          style: FilledButton.styleFrom(
            backgroundColor: AppColors.careenaTeal,
            foregroundColor: Colors.white,
          ),
          onPressed: _nameController.text.trim().isEmpty ? null : _save,
          child: const Text('Speichern'),
        ),
      ],
    );
  }

  void _save() {
    final name = _nameController.text.trim();
    if (name.isEmpty) return;
    Navigator.pop(context, name);
  }
}
