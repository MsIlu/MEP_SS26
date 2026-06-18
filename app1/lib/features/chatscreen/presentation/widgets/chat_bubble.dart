import 'package:flutter/material.dart';
import '../../../../core/config/app_assets.dart';
import '../../data/models/message_model.dart';
import 'package:app1/core/themes/app_colors.dart';
import 'medical_term_tooltip_text.dart';
import 'thinking_bubble.dart';
import '../../../recommendation_export/presentation/create_recommended_appointment_button.dart';
import '../../../recommendation_export/presentation/export_recommendation_pdf_button.dart';
import 'recommendation_summary_card.dart';

/// UI component that displays a single chat message.
///
/// This widget handles:
/// - Differentiating between user and assistant messages
/// - Rendering loading states (thinking indicator)
/// - Styling chat bubbles based on sender
class ChatBubble extends StatelessWidget {
  final Message message;
  final bool showLongProcessingHint;

  const ChatBubble({
    super.key,
    required this.message,
    this.showLongProcessingHint = false,
  });

  @override
  Widget build(BuildContext context) {
    final isUser = message.isUser;
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    final avatarBackground = isDarkMode
        ? const Color(0xFF86B2B2)
        : const Color(0xFFC3E7E7);

    final bubbleColor = isUser
        ? AppColors.careenaTeal
        : isDarkMode
        ? colorScheme.surface
        : Colors.white;

    final textColor = isUser
        ? Colors.white
        : isDarkMode
        ? colorScheme.onSurface
        : AppColors.careenaDark;

    final shadowColor = isDarkMode
        ? Colors.black.withValues(alpha: 0.15)
        : Colors.black.withValues(alpha: 0.10);
    final showRecommendationCard =
        !isUser && message.canExportPdf && !message.isStreaming;

    // Show the animated indicator while the assistant response is pending.
    if (message.isLoading) {
      return ThinkingBubble(showLongProcessingHint: showLongProcessingHint);
    }

    return LayoutBuilder(
      builder: (context, constraints) {
        final bubbleMaxWidth = constraints.maxWidth < 420
            ? constraints.maxWidth * 0.78
            : showRecommendationCard
            ? constraints.maxWidth * 0.92
            : constraints.maxWidth * 0.68;

        return Padding(
          padding: const EdgeInsets.symmetric(vertical: 8.0, horizontal: 12.0),
          child: Row(
            mainAxisAlignment: isUser
                ? MainAxisAlignment.end
                : MainAxisAlignment.start,
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              // Assistant avatar.
              if (!isUser) ...[
                CircleAvatar(
                  radius: 16,
                  backgroundColor: avatarBackground,
                  child: Padding(
                    padding: const EdgeInsets.all(2),
                    child: Image.asset(
                      AppAssets.careenaProfil,
                      fit: BoxFit.contain,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
              ],
              ConstrainedBox(
                constraints: BoxConstraints(maxWidth: bubbleMaxWidth),
                child: Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 12,
                  ),
                  decoration: BoxDecoration(
                    color: bubbleColor,
                    borderRadius: BorderRadius.only(
                      topLeft: const Radius.circular(20),
                      topRight: const Radius.circular(20),
                      bottomLeft: Radius.circular(isUser ? 20 : 4),
                      bottomRight: Radius.circular(isUser ? 4 : 20),
                    ),

                    border: !isUser && !isDarkMode
                        ? Border.all(color: Colors.grey.shade200, width: 1)
                        : null,

                    boxShadow: [
                      BoxShadow(
                        color: shadowColor,
                        blurRadius: 12,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      if (showRecommendationCard)
                        RecommendationSummaryCard(
                          recommendation:
                              message.exportRecommendation ?? message.text,
                        )
                      else
                        MedicalTermTooltipText(
                          text: message.text,
                          enabled: !isUser,
                          style: TextStyle(color: textColor, fontSize: 15),
                        ),
                      if (showRecommendationCard) ...[
                        const SizedBox(height: 12),
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            SizedBox(
                              width: double.infinity,
                              child: ExportRecommendationPdfButton(
                                title:
                                    message.exportTitle ??
                                    'Handlungsempfehlung',
                                patientSummary:
                                    'Aus dem Chatverlauf generierte Handlungsempfehlung.',
                                recommendation:
                                    message.exportRecommendation ??
                                    message.text,
                                nextSteps: message.exportNextSteps ?? '',
                              ),
                            ),
                            if (message.canCreateAppointment) ...[
                              const SizedBox(height: 8),
                              SizedBox(
                                width: double.infinity,
                                child: CreateRecommendedAppointmentButton(
                                  title:
                                      message.appointmentTitle ??
                                      'Arzttermin vereinbaren',
                                ),
                              ),
                            ],
                          ],
                        ),
                      ],
                    ],
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}
