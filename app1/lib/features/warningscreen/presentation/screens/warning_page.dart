import 'package:flutter/material.dart';
import '../../../../core/widgets/responsive_frame.dart';
import '../../../chatscreen/data/models/chat_response_model.dart';
import 'package:app1/core/themes/app_colors.dart';
import '../theme/warning_copy.dart';
import '../theme/warning_layout.dart';
import '../theme/warning_theme.dart';
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

    final appBarColor = isDarkMode
        ? colorScheme.surface
        : Colors.white;

    final titleColor = isDarkMode
        ? colorScheme.onSurface
        : WarningColors.darkText;

    final iconColor = isDarkMode
        ? AppColors.toolbarButtonBackgroundDark
        : WarningColors.teal;

    return Scaffold(
      backgroundColor: backgroundColor,
      appBar: AppBar(
        elevation: 0,
        backgroundColor: appBarColor,
        centerTitle: true,
        leading: IconButton(
          icon: Icon(Icons.chevron_left, color: iconColor),
          iconSize: 32,
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          WarningCopy.pageTitle,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: TextStyle(
            color: titleColor,
            fontWeight: FontWeight.bold,
            fontSize: 18,
          ),
        ),
      ),
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
                patientSummary: 'Aus dem Chatverlauf generierte Handlungsempfehlung.',
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