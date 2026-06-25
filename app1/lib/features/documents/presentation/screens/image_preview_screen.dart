import 'dart:typed_data';
import 'package:share_plus/share_plus.dart';

import 'package:app1/core/themes/app_colors.dart';
import 'package:app1/core/widgets/careena_page_header.dart';
import 'package:flutter/material.dart';

class ImagePreviewScreen extends StatelessWidget {
  final String documentName;
  final Uint8List fileBytes;
  final String mimeType;

  const ImagePreviewScreen({
    super.key,
    required this.documentName,
    required this.fileBytes,
    required this.mimeType,
  });

  Future<void> _shareImage() async {
    await SharePlus.instance.share(
      ShareParams(
        files: [
          XFile.fromData(fileBytes, name: documentName, mimeType: mimeType),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: CareenaPageHeader(title: documentName),
      body: Container(
        color: Colors.black,
        alignment: Alignment.center,
        child: InteractiveViewer(
          minScale: 0.8,
          maxScale: 5,
          child: Image.memory(
            fileBytes,
            fit: BoxFit.contain,
            errorBuilder: (context, error, stackTrace) {
              return const Center(
                child: Text(
                  'Das Bild konnte nicht angezeigt werden.',
                  style: TextStyle(color: Colors.white),
                ),
              );
            },
          ),
        ),
      ),
      bottomNavigationBar: SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(20, 12, 20, 16),
          child: FilledButton.icon(
            onPressed: _shareImage,
            icon: const Icon(Icons.ios_share_outlined),
            label: const Text('Teilen'),
            style: FilledButton.styleFrom(
              backgroundColor: AppColors.careenaTeal,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 14),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(14),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
