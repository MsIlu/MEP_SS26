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
      title: const Text(
        'Dokument hinzufügen',
        style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
      ),
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
                cursorColor: AppColors.careenaTeal,
                maxLength: 100,
                decoration: InputDecoration(
                  labelText: 'Dokumentname',
                  hintText: 'z. B. Blutwerte Juni 2026',
                  prefixIcon: const Icon(Icons.description_outlined),
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
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<DocumentCategory>(
                initialValue: _category,
                decoration: InputDecoration(
                  labelText: 'Kategorie',
                  prefixIcon: const Icon(Icons.folder_outlined),
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
          style: TextButton.styleFrom(foregroundColor: AppColors.careenaTeal),
          onPressed: () => Navigator.pop(context),
          child: const Text('Abbrechen'),
        ),
        FilledButton.icon(
          style: FilledButton.styleFrom(
            backgroundColor: AppColors.careenaTeal,
            foregroundColor: Colors.white,
          ),
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
