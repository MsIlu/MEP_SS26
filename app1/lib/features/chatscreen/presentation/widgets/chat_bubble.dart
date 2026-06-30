import 'package:flutter/material.dart';
import '../../../../core/config/app_assets.dart';
import '../../data/models/message_model.dart';
import 'package:app1/core/themes/app_colors.dart';
import 'thinking_bubble.dart';
import '../../../recommendation_export/presentation/create_recommended_appointment_button.dart';
import '../../../recommendation_export/presentation/export_recommendation_pdf_button.dart';
import '../../../recommendation_export/presentation/save_recommendation_to_documents_button.dart';
import '../../../authscreen/state/auth_session.dart';

/// UI component that displays a single chat message.
///
/// This widget handles:
/// - Differentiating between user and assistant messages
/// - Rendering loading states (thinking indicator)
/// - Styling chat bubbles based on sender
class ChatBubble extends StatelessWidget {
  final Message message;
  final List<String> symptoms;
  final List<String> userMessages;
  final bool showLongProcessingHint;
  final AuthSession? authSession;
  final String? recommendationSessionId;
  final Future<void> Function(Message, RecommendationAction)?
  onRecommendationAction;
  final VoidCallback? onSaveSymptoms;

  const ChatBubble({
    super.key,
    required this.message,
    required this.symptoms,
    required this.userMessages,
    this.showLongProcessingHint = false,
    this.authSession,
    this.recommendationSessionId,
    this.onRecommendationAction,
    this.onSaveSymptoms,
  });

  @override
  Widget build(BuildContext context) {
    final isUser = message.isUser;
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    final avatarBackground = isDarkMode
        ? AppColors.chatAvatarBackgroundDark
        : AppColors.chatAvatarBackgroundLight;

    final bubbleColor = isUser
        ? AppColors.careenaTeal
        : isDarkMode
        ? colorScheme.surface
        : AppColors.white;

    final textColor = isUser
        ? AppColors.white
        : isDarkMode
        ? colorScheme.onSurface
        : AppColors.careenaDark;

    final shadowColor = isDarkMode
        ? AppColors.black.withValues(alpha: 0.15)
        : AppColors.black.withValues(alpha: 0.10);
    final recommendationSymptoms = message.recommendationSymptoms.isNotEmpty
        ? message.recommendationSymptoms
        : symptoms;

    // Show the animated indicator while the assistant response is pending.
    if (message.isLoading) {
      return ThinkingBubble(showLongProcessingHint: showLongProcessingHint);
    }

    return LayoutBuilder(
      builder: (context, constraints) {
        final bubbleMaxWidth = constraints.maxWidth < 420
            ? constraints.maxWidth * 0.78
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
                        ? Border.all(color: AppColors.greyShade200, width: 1)
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
                      Text(
                        message.text,
                        style: TextStyle(color: textColor, fontSize: 15),
                      ),
                      if (!isUser &&
                          message.canExportPdf &&
                          !message.isStreaming) ...[
                        const SizedBox(height: 12),
                        Wrap(
                          spacing: 8,
                          runSpacing: 8,
                          children: [
                            SaveRecommendationToDocumentsButton(
                              title:
                                  message.exportTitle ?? 'Handlungsempfehlung',
                              patientSummary:
                                  'Zusammenfassung des Chatverlaufes',
                              recommendation:
                                  message.exportRecommendation ?? message.text,
                              nextSteps: message.exportNextSteps ?? '',
                              symptoms: recommendationSymptoms,
                              userMessages: userMessages,
                              alreadySaved: message.documentSaved,
                              onSaved: () => onRecommendationAction?.call(
                                message,
                                RecommendationAction.document,
                              ),
                            ),
                            ExportRecommendationPdfButton(
                              title:
                                  message.exportTitle ?? 'Handlungsempfehlung',
                              patientSummary:
                                  'Zusammenfassung des Chatverlaufes',
                              recommendation:
                                  message.exportRecommendation ?? message.text,
                              nextSteps: message.exportNextSteps ?? '',
                              symptoms: recommendationSymptoms,
                              userMessages: userMessages,
                            ),
                            if (message.canCreateAppointment)
                              CreateRecommendedAppointmentButton(
                                title:
                                    message.appointmentTitle ??
                                    'Arzttermin vereinbaren',
                                authSession: authSession,
                                sessionId: recommendationSessionId,
                                alreadySearched: message.appointmentSearched,
                                onSearched: () => onRecommendationAction?.call(
                                  message,
                                  RecommendationAction.appointment,
                                ),
                              ),
                            if (recommendationSymptoms.isNotEmpty)
                              OutlinedButton.icon(
                                style: OutlinedButton.styleFrom(
                                  foregroundColor: AppColors.careenaTeal,
                                  side: const BorderSide(
                                    color: AppColors.careenaTeal,
                                  ),
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: 18,
                                    vertical: 14,
                                  ),
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(18),
                                  ),
                                ),
                                onPressed: message.symptomsSaved
                                    ? null
                                    : onSaveSymptoms,
                                icon: Icon(
                                  message.symptomsSaved
                                      ? Icons.check_circle_outline
                                      : Icons.book_outlined,
                                ),
                                label: Text(
                                  message.symptomsSaved
                                      ? 'Symptome bereits gespeichert – siehe Tagebuch'
                                      : 'Symptome ins Tagebuch',
                                ),
                              ),
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
