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
    final showEmergencyActions = _showEmergencyActions(response);

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
              if (showEmergencyActions)
                EmergencyCard(response: response)
              else
                _RecommendationCard(response: response),
              const SizedBox(height: 16),

              ExportRecommendationPdfButton(
                title: WarningCopy.pageTitle,
                patientSummary:
                    'Aus dem Chatverlauf generierte Handlungsempfehlung.',
                recommendation: _recommendationTextFor(response),
                nextSteps:
                    response.recommendationResult?.nextStep ??
                    response.action ??
                    'Bitte folgen Sie den angezeigten Handlungsschritten. Bei akuter Gefahr kontaktieren Sie den Notruf 112.',
                symptoms: const [],
                userMessages: const [],
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

bool _showEmergencyActions(ChatResponse response) {
  final combined = '${response.text} ${response.action ?? ''}'
      ' ${response.severity ?? ''} ${response.category ?? ''}'
      .toLowerCase();
  return response.redFlag ||
      combined.contains('notruf') ||
      combined.contains('112') ||
      combined.contains('notaufnahme') ||
      combined.contains('sofort');
}

String _recommendationTextFor(ChatResponse response) {
  final chatText = response.text.trim();
  if (chatText.isNotEmpty) {
    return chatText;
  }
  return response.recommendationResult?.summary ?? '';
}

class _RecommendationCard extends StatelessWidget {
  final ChatResponse response;

  const _RecommendationCard({required this.response});

  @override
  Widget build(BuildContext context) {
    final recommendation = response.recommendationResult;
    final colorScheme = Theme.of(context).colorScheme;
    final reasons = recommendation?.reasons ?? const <String>[];
    final limitations = recommendation?.limitations ?? const <String>[];
    final nextStep = recommendation?.nextStep ?? response.action;
    final recommendationText = _recommendationTextFor(response);
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    final accent = AppColors.primary;

    return Container(
      padding: WarningLayout.cardPadding,
      decoration: BoxDecoration(
        color: colorScheme.surface,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: isDarkMode
              ? accent.withValues(alpha: 0.72)
              : accent.withValues(alpha: 0.42),
          width: 1.4,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: isDarkMode ? 0.18 : 0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              CircleAvatar(
                radius: 42,
                backgroundColor: accent.withValues(alpha: 0.14),
                child: Icon(
                  Icons.medical_information_outlined,
                  color: accent,
                  size: 40,
                ),
              ),
              const SizedBox(width: 22),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text(
                      'Ihre Handlungsempfehlung',
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            color: accent,
                            fontWeight: FontWeight.w900,
                          ),
                    ),
                    const SizedBox(height: 14),
                    Text(
                      recommendationText,
                      style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                            fontWeight: FontWeight.w700,
                            height: 1.35,
                          ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 22),
          _RecommendationDivider(color: accent),
          const SizedBox(height: 18),
          Text(
            'Was sollten Sie jetzt tun?',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w900,
                ),
          ),
          if (nextStep != null && nextStep.trim().isNotEmpty) ...[
            const SizedBox(height: 16),
            _RecommendationActionRow(
              icon: Icons.event_available_outlined,
              text: nextStep,
              color: accent,
            ),
          ],
          if (reasons.isNotEmpty) ...[
            const SizedBox(height: 16),
            _RecommendationDivider(color: accent),
            const SizedBox(height: 16),
            _RecommendationActionRow(
              icon: Icons.fact_check_outlined,
              text: reasons.join('\n'),
              color: accent,
              title: 'Gründe',
            ),
          ],
          if (limitations.isNotEmpty) ...[
            const SizedBox(height: 16),
            _RecommendationDivider(color: accent),
            const SizedBox(height: 16),
            _RecommendationActionRow(
              icon: Icons.info_outline,
              text: limitations.join('\n'),
              color: accent,
              title: 'Hinweise',
            ),
          ],
        ],
      ),
    );
  }
}

class _RecommendationActionRow extends StatelessWidget {
  final IconData icon;
  final String text;
  final Color color;
  final String? title;

  const _RecommendationActionRow({
    required this.icon,
    required this.text,
    required this.color,
    this.title,
  });

  @override
  Widget build(BuildContext context) {
    final lines = text
        .split('\n')
        .map((line) => line.trim())
        .where((line) => line.isNotEmpty)
        .toList(growable: false);

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        CircleAvatar(
          radius: 18,
          backgroundColor: color.withValues(alpha: 0.12),
          child: Icon(icon, color: color, size: 20),
        ),
        const SizedBox(width: 14),
        Expanded(
          child: Padding(
            padding: const EdgeInsets.only(top: 3),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                if (title != null) ...[
                  Text(
                    title!,
                    style: const TextStyle(fontWeight: FontWeight.w900),
                  ),
                  const SizedBox(height: 6),
                ],
                for (final line in lines)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 4),
                    child: Text(
                      title == null ? line : '• $line',
                      style: const TextStyle(height: 1.35),
                    ),
                  ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}

class _RecommendationDivider extends StatelessWidget {
  final Color color;

  const _RecommendationDivider({required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 1,
      color: color.withValues(alpha: 0.28),
    );
  }
}
