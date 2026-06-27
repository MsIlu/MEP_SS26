import 'package:app1/app/app_dependencies_scope.dart';
import 'package:app1/features/profiles/domain/models/profile.dart';
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
  final List<String> symptoms;
  final List<String> userMessages;

  const ExportRecommendationPdfButton({
    super.key,
    required this.title,
    required this.patientSummary,
    required this.recommendation,
    required this.nextSteps,
    required this.symptoms,
    required this.userMessages,
  });

  @override
  Widget build(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    final buttonColor = isDarkMode
        ? AppColors.toolbarButtonBackgroundDark
        : AppColors.careenaTeal;

    final textColor = isDarkMode
        ? AppColors.toolbarButtonForegroundDark
        : AppColors.white;

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
        final dependencies = AppDependenciesScope.maybeOf(context);
        final authSession = dependencies?.authSession;
        final profileApiService = dependencies?.profileApiService;
        final activeProfileId = authSession?.activeProfileId;

        Profile? profile;

        if (activeProfileId != null && profileApiService != null) {
          try {
            profile = await profileApiService.getProfile(activeProfileId);
          } catch (_) {
            profile = null;
          }
        }

        final pdfService = RecommendationPdfService();

        final pdfBytes = await pdfService.buildRecommendationPdf(
          title: title,
          patientSummary: patientSummary,
          recommendation: recommendation,
          nextSteps: nextSteps,
          symptoms: symptoms,
          profile: profile,
          userMessages: userMessages,
        );

        await Printing.layoutPdf(
          name: 'versorgungsempfehlung.pdf',
          onLayout: (_) async => pdfBytes,
        );
      },
    );
  }
}