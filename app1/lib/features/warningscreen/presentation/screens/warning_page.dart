import 'package:flutter/material.dart';
import '../../../../core/widgets/responsive_frame.dart';
import '../../../../core/widgets/careena_page_header.dart';
import '../../../chatscreen/data/models/chat_response_model.dart';
import 'package:app1/core/themes/app_colors.dart';
import '../theme/warning_copy.dart';
import '../theme/warning_layout.dart';
import '../widgets/emergency_card.dart';
import '../widgets/no_diagnosis_info_box.dart';
import '../../../recommendation_export/presentation/export_recommendation_pdf_button.dart';

/// Safety page shown when the backend detects a red-flag response.
class WarningPage extends StatelessWidget {
  /// Backend response that contains the red-flag metadata.
  final ChatResponse response;

  const WarningPage({super.key, required this.response});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    final backgroundColor = isDarkMode
        ? colorScheme.surface
        : AppColors.background;

    return Scaffold(
      backgroundColor: backgroundColor,
      appBar: const CareenaPageHeader(title: WarningCopy.pageTitle),
      body: SafeArea(
        child: ResponsivePageBody(
          maxWidth: WarningLayout.maxContentWidth,
          scrollable: true,
          padding: WarningLayout.pagePadding,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              EmergencyCard(response: response),
              const SizedBox(height: 16),

              ExportRecommendationPdfButton(
                title: WarningCopy.pageTitle,
                patientSummary:
                    'Aus dem Chatverlauf generierte Handlungsempfehlung.',
                recommendation: response.text,
                nextSteps:
                    response.action ??
                    'Bitte folgen Sie den angezeigten Handlungsschritten. Bei akuter Gefahr kontaktieren Sie den Notruf 112.',
              ),

              const SizedBox(height: 16),
              const NoDiagnosisInfoBox(),
            ],
          ),
        ),
      ),
    );
  }
}
