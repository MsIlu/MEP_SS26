import 'package:flutter/material.dart';
import '../../../../core/config/app_assets.dart';
import '../../data/models/message_model.dart';
import '../../utils/medical_terms.dart';
import '../themes/app_colors.dart';
import 'medical_term_info_box.dart';
import 'thinking_bubble.dart';
import '../../../recommendation_export/presentation/export_recommendation_pdf_button.dart';

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
    final medicalTerm = isUser ? null : MedicalTerms.firstMatch(message.text);
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

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
        : Colors.black.withValues(alpha: 0.05);

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
                const CircleAvatar(
                  radius: 16,
                  backgroundColor: AppColors.careenaBubbleBackground,
                  backgroundImage: AssetImage(AppAssets.careenaDoctor),
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
                    boxShadow: [
                      BoxShadow(
                        color: shadowColor,
                        blurRadius: 5,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        message.text,
                        style: TextStyle(
                          color: textColor,
                          fontSize: 15,
                        ),
                      ),
                      if (medicalTerm != null)
                        MedicalTermInfoBox(term: medicalTerm),
                      if (!isUser && message.canExportPdf && !message.isStreaming) ...[
                        const SizedBox(height: 12),
                        ExportRecommendationPdfButton(
                          title: message.exportTitle ?? 'Handlungsempfehlung',
                          patientSummary:
                          'Aus dem Chatverlauf generierte Handlungsempfehlung.',
                          recommendation: message.exportRecommendation ?? message.text,
                          nextSteps: message.exportNextSteps ?? '',
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
