import 'package:flutter/material.dart';
import 'package:printing/printing.dart';
import 'package:app1/core/themes/app_colors.dart';
import '../data/recommendation_pdf_service.dart';

/// Button that exports a generated care recommendation as a PDF.
class ExportRecommendationPdfButton extends StatelessWidget {
  final String title;
  final String patientSummary;
  final String recommendation;
  final String nextSteps;

  const ExportRecommendationPdfButton({
    super.key,
    required this.title,
    required this.patientSummary,
    required this.recommendation,
    required this.nextSteps,
  });

  @override
  Widget build(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    final buttonColor = isDarkMode
        ? AppColors.toolbarButtonBackgroundDark
        : AppColors.careenaTeal;

    final textColor = isDarkMode
        ? AppColors.toolbarButtonForegroundDark
        : Colors.white;

    return FilledButton.icon(
      style: FilledButton.styleFrom(
        backgroundColor: buttonColor,
        foregroundColor: textColor,
        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
      ),
      icon: const Icon(Icons.picture_as_pdf),
      label: const Text('PDF exportieren'),
      onPressed: () async {
        final pdfService = RecommendationPdfService();

        final pdfBytes = await pdfService.buildRecommendationPdf(
          title: title,
          patientSummary: patientSummary,
          recommendation: recommendation,
          nextSteps: nextSteps,
        );

        await Printing.layoutPdf(
          name: 'versorgungsempfehlung.pdf',
          onLayout: (_) async => pdfBytes,
        );
      },
    );
  }
}
