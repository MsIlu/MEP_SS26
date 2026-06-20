import 'package:app1/core/themes/app_colors.dart';
import 'package:flutter/material.dart';

import '../../data/models/document_entry.dart';

class UploadDocumentDraft {
  final String name;
  final DocumentCategory category;

  const UploadDocumentDraft({required this.name, required this.category});
}

class UploadDocumentDialog extends StatefulWidget {
  const UploadDocumentDialog({super.key});

  @override
  State<UploadDocumentDialog> createState() => _UploadDocumentDialogState();
}

class _UploadDocumentDialogState extends State<UploadDocumentDialog> {
  final _nameController = TextEditingController();
  DocumentCategory _category = DocumentCategory.findings;

  @override
  void dispose() {
    _nameController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      insetPadding: const EdgeInsets.all(24),
      icon: const Icon(
        Icons.upload_file_outlined,
        color: AppColors.careenaTeal,
        size: 36,
      ),
      title: const Text('Dokument hinzufügen'),
      content: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 420),
        child: SizedBox(
          width: double.maxFinite,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              TextField(
                controller: _nameController,
                autofocus: true,
                maxLength: 100,
                decoration: const InputDecoration(
                  labelText: 'Dokumentname',
                  hintText: 'z. B. Blutwerte Juni 2026',
                  prefixIcon: Icon(Icons.description_outlined),
                ),
                onChanged: (_) => setState(() {}),
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<DocumentCategory>(
                initialValue: _category,
                decoration: const InputDecoration(
                  labelText: 'Kategorie',
                  prefixIcon: Icon(Icons.folder_outlined),
                ),
                items: [
                  for (final category in DocumentCategory.values)
                    DropdownMenuItem(
                      value: category,
                      child: Text(category.label),
                    ),
                ],
                onChanged: (category) {
                  if (category != null) {
                    setState(() => _category = category);
                  }
                },
              ),
            ],
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Abbrechen'),
        ),
        FilledButton.icon(
          onPressed: _nameController.text.trim().isEmpty
              ? null
              : () => Navigator.pop(
                  context,
                  UploadDocumentDraft(
                    name: _nameController.text.trim(),
                    category: _category,
                  ),
                ),
          icon: const Icon(Icons.add),
          label: const Text('Hinzufügen'),
        ),
      ],
    );
  }
}
