import 'dart:typed_data';

import 'package:app1/core/themes/app_colors.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../../data/models/document_entry.dart';

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

  final ImagePicker _imagePicker = ImagePicker();

  Uint8List? _selectedBytes;
  String? _selectedName;
  String? _selectedMimeType;
  String? _fileError;

  @override
  void dispose() {
    _nameController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

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
              Row(
                children: [
                  Expanded(
                    child: _SourceButton(
                      icon: Icons.attach_file,
                      label: 'Datei',
                      onPressed: _pickFile,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: _SourceButton(
                      icon: Icons.photo_library_outlined,
                      label: 'Foto',
                      onPressed: () => _pickImage(ImageSource.gallery),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: _SourceButton(
                      icon: Icons.camera_alt_outlined,
                      label: 'Kamera',
                      onPressed: () => _pickImage(ImageSource.camera),
                    ),
                  ),
                ],
              ),

              if (_selectedName != null) ...[
                const SizedBox(height: 10),
                Text(
                  _selectedName!,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
              if (_fileError != null) ...[
                const SizedBox(height: 6),
                Text(_fileError!, style: const TextStyle(color: Colors.red)),
              ],
              const SizedBox(height: 12),
              TextField(
                controller: _nameController,
                autofocus: true,
                cursorColor: colorScheme.onSurface,
                maxLength: 100,
                decoration: InputDecoration(
                  labelText: 'Dokumentname',
                  hintText: 'z. B. Blutwerte Juni 2026',
                  prefixIcon: const Icon(Icons.description_outlined),
                  floatingLabelStyle: TextStyle(
                    color: colorScheme.onSurface,
                    fontWeight: FontWeight.w600,
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(14),
                    borderSide: BorderSide(
                      color: AppColors.greyShade400,
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
                  floatingLabelStyle: TextStyle(
                    color: colorScheme.onSurface,
                    fontWeight: FontWeight.w600,
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(14),
                    borderSide: BorderSide(
                      color: AppColors.greyShade400,
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
              _selectedBytes == null ||
                  _selectedMimeType == null ||
                  _nameController.text.trim().isEmpty
              ? null
              : () {
                  Navigator.pop(
                    context,
                    UploadDocumentDraft(
                      name: _nameController.text.trim(),
                      category: _category,
                      fileBytes: _selectedBytes!,
                      mimeType: _selectedMimeType!,
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
    try {
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
          _clearSelectedDocument();
          _fileError = 'Die Datei konnte nicht gelesen werden.';
        });
        return;
      }

      final extension = file.extension?.toLowerCase();

      _selectDocument(
        bytes: bytes,
        name: file.name,
        mimeType: switch (extension) {
          'pdf' => 'application/pdf',
          'jpg' || 'jpeg' => 'image/jpeg',
          'png' => 'image/png',
          _ => 'application/octet-stream',
        },
      );
    } catch (_) {
      if (!mounted) return;

      setState(() {
        _clearSelectedDocument();
        _fileError =
            'Die Datei konnte nicht ausgewählt werden. Bitte versuche es erneut.';
      });
    }
  }

  Future<void> _pickImage(ImageSource source) async {
    try {
      final image = await _imagePicker.pickImage(
        source: source,
        imageQuality: 85,
      );

      if (image == null) return;

      final bytes = await image.readAsBytes();
      final extension = image.name.split('.').last.toLowerCase();

      _selectDocument(
        bytes: bytes,
        name: image.name,
        mimeType: extension == 'png' ? 'image/png' : 'image/jpeg',
      );
    } catch (_) {
      if (!mounted) return;

      setState(() {
        _clearSelectedDocument();
        _fileError = source == ImageSource.camera
            ? 'Die Kamera konnte nicht geöffnet werden. Prüfe die Kameraberechtigung.'
            : 'Die Fotomediathek konnte nicht geöffnet werden. Prüfe die Fotoberechtigung.';
      });
    }
  }

  void _selectDocument({
    required Uint8List bytes,
    required String name,
    required String mimeType,
  }) {
    const maximumSize = 10 * 1024 * 1024;

    if (bytes.lengthInBytes > maximumSize) {
      setState(() {
        _clearSelectedDocument();
        _fileError = 'Die Datei darf maximal 10 MB groß sein.';
      });
      return;
    }

    setState(() {
      _selectedBytes = bytes;
      _selectedName = name;
      _selectedMimeType = mimeType;
      _fileError = null;
      _nameController.text = name;
    });
  }

  void _clearSelectedDocument() {
    _selectedBytes = null;
    _selectedName = null;
    _selectedMimeType = null;
  }
}

class _SourceButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onPressed;

  const _SourceButton({
    required this.icon,
    required this.label,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return OutlinedButton(
      onPressed: onPressed,
      style: OutlinedButton.styleFrom(
        foregroundColor: AppColors.careenaTeal,
        side: const BorderSide(color: AppColors.careenaTeal, width: 1.5),
        padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 12),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 22),
          const SizedBox(height: 4),
          Text(
            label,
            maxLines: 1,
            style: const TextStyle(fontWeight: FontWeight.w600),
          ),
        ],
      ),
    );
  }
}
