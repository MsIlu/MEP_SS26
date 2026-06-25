import 'dart:typed_data';

import 'package:app1/core/themes/app_colors.dart';
import 'package:app1/core/widgets/careena_page_header.dart';
import 'package:flutter/material.dart';
import 'package:printing/printing.dart';

class DocumentPreviewScreen extends StatelessWidget {
  final String documentName;
  final Uint8List fileBytes;

  const DocumentPreviewScreen({
    super.key,
    required this.documentName,
    required this.fileBytes,
  });

 @override
Widget build(BuildContext context) {
  return Scaffold(
    appBar: CareenaPageHeader(
      title: documentName,
    ),
    body: PdfPreview(
      build: (_) async => fileBytes,
      canChangePageFormat: false,
      canChangeOrientation: false,
      canDebug: false,
      allowPrinting: false,
      allowSharing: false,
      pdfPreviewPageDecoration: BoxDecoration(
        color: Colors.white,
        boxShadow: const [
          BoxShadow(
            color: Colors.black26,
            blurRadius: 8,
            offset: Offset(0, 3),
          ),
        ],
      ),
      loadingWidget: const Center(
        child: CircularProgressIndicator(
          color: AppColors.careenaTeal,
        ),
      ),
    ),
    bottomNavigationBar: SafeArea(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(20, 12, 20, 16),
        child: Row(
          children: [
            Expanded(
              child: OutlinedButton.icon(
                onPressed: () => Printing.sharePdf(
                  bytes: fileBytes,
                  filename: documentName,
                ),
                icon: const Icon(Icons.ios_share_outlined),
                label: const Text('Teilen'),
                style: OutlinedButton.styleFrom(
                  foregroundColor: AppColors.careenaTeal,
                  side: const BorderSide(
                    color: AppColors.careenaTeal,
                    width: 1.5,
                  ),
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14),
                  ),
                ),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: FilledButton.icon(
                onPressed: () => Printing.layoutPdf(
                  name: documentName,
                  onLayout: (_) async => fileBytes,
                ),
                icon: const Icon(Icons.print_outlined),
                label: const Text('Drucken'),
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
          ],
        ),
      ),
    ),
  );
}
}