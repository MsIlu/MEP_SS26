import 'package:app1/core/themes/app_colors.dart';
import 'package:flutter/material.dart';

import '../../data/models/document_entry.dart';
import 'dart:typed_data';
import 'package:file_picker/file_picker.dart';

class UploadDocumentDraft {
  final String name;
  final DocumentCategory category;
  final Uint8List fileBytes;
  final String mimeType;

  const UploadDocumentDraft({
    required this.name,
    required this.category,
    required this.fileBytes,
    required this.mimeType,
  });
}

class UploadDocumentDialog extends StatefulWidget {
  const UploadDocumentDialog({super.key});

  @override
  State<UploadDocumentDialog> createState() => _UploadDocumentDialogState();
}

class _UploadDocumentDialogState extends State<UploadDocumentDialog> {
  final _nameController = TextEditingController();
  DocumentCategory _category = DocumentCategory.findings;

  PlatformFile? _selectedFile;
  String? _fileError;

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
              OutlinedButton.icon(
                onPressed: _pickFile,
                icon: const Icon(Icons.attach_file),
                label: Text(
                  _selectedFile == null
                      ? 'Datei auswählen'
                      : _selectedFile!.name,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                style: OutlinedButton.styleFrom(
                  foregroundColor: AppColors.careenaTeal,
                  side: const BorderSide(color: AppColors.careenaTeal),
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14),
                  ),
                ),
              ),
              if (_fileError != null) ...[
                const SizedBox(height: 6),
                Text(_fileError!, style: const TextStyle(color: Colors.red)),
              ],
              const SizedBox(height: 12),
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
          onPressed:
              _selectedFile == null || _nameController.text.trim().isEmpty
              ? null
              : () {
                  final file = _selectedFile!;
                  final extension = file.extension?.toLowerCase();

                  Navigator.pop(
                    context,
                    UploadDocumentDraft(
                      name: _nameController.text.trim(),
                      category: _category,
                      fileBytes: file.bytes!,
                      mimeType: switch (extension) {
                        'pdf' => 'application/pdf',
                        'jpg' || 'jpeg' => 'image/jpeg',
                        'png' => 'image/png',
                        _ => 'application/octet-stream',
                      },
                    ),
                  );
                },
          icon: const Icon(Icons.add),
          label: const Text('Hinzufügen'),
        ),
      ],
    );
  }

  Future<void> _pickFile() async {
    final result = await FilePicker.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf', 'jpg', 'jpeg', 'png'],
      withData: true,
    );

    if (result == null) return;

    final file = result.files.single;
    final bytes = file.bytes;

    if (bytes == null) {
      setState(() {
        _fileError = 'Die Datei konnte nicht gelesen werden.';
      });
      return;
    }

    const maximumSize = 10 * 1024 * 1024;

    if (bytes.lengthInBytes > maximumSize) {
      setState(() {
        _fileError = 'Die Datei darf maximal 10 MB groß sein.';
      });
      return;
    }

    setState(() {
      _selectedFile = file;
      _fileError = null;
      _nameController.text = file.name;
    });
  }
}
