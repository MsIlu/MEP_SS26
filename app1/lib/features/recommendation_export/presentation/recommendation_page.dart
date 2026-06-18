import 'package:app1/core/themes/app_colors.dart';
import 'package:app1/core/widgets/careena_page_header.dart';
import 'package:app1/core/widgets/responsive_frame.dart';
import 'package:app1/features/chatscreen/data/models/chat_response_model.dart';
import 'package:app1/features/chatscreen/presentation/widgets/recommendation_summary_card.dart';
import 'package:app1/features/recommendation_export/presentation/create_recommended_appointment_button.dart';
import 'package:app1/features/recommendation_export/presentation/export_recommendation_pdf_button.dart';
import 'package:app1/features/warningscreen/presentation/theme/warning_copy.dart';
import 'package:app1/features/warningscreen/presentation/theme/warning_layout.dart';
import 'package:app1/features/warningscreen/presentation/widgets/no_diagnosis_info_box.dart';
import 'package:flutter/material.dart';

/// Dedicated screen for non-emergency care recommendations.
class RecommendationPage extends StatelessWidget {
  final ChatResponse response;
  final bool canCreateAppointment;
  final String? appointmentTitle;

  const RecommendationPage({
    super.key,
    required this.response,
    required this.canCreateAppointment,
    this.appointmentTitle,
  });

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
              RecommendationSummaryCard(recommendation: response.text),
              const SizedBox(height: 16),
              ExportRecommendationPdfButton(
                title: WarningCopy.pageTitle,
                patientSummary:
                    'Aus dem Chatverlauf generierte Handlungsempfehlung.',
                recommendation: response.text,
                nextSteps: response.action ?? '',
              ),
              if (canCreateAppointment) ...[
                const SizedBox(height: 12),
                CreateRecommendedAppointmentButton(
                  title: appointmentTitle ?? 'Arzttermin vereinbaren',
                ),
              ],
              const SizedBox(height: 16),
              const NoDiagnosisInfoBox(),
            ],
          ),
        ),
      ),
    );
  }
}
