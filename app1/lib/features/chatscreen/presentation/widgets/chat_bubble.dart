import 'package:flutter/material.dart';
import '../../../../core/config/app_assets.dart';
import '../../data/models/message_model.dart';
import '../../utils/medical_terms.dart';
import 'medical_term_info_box.dart';
import 'thinking_bubble.dart';

/// UI component that displays a single chat message.
///
/// This widget handles:
/// - Differentiating between user and assistant messages
/// - Rendering loading states (thinking indicator)
/// - Styling chat bubbles based on sender
class ChatBubble extends StatelessWidget {
  final Message message;
  final bool showLongProcessingHint;
  final VoidCallback? onCancelGeneration;

  const ChatBubble({
    super.key,
    required this.message,
    this.showLongProcessingHint = false,
    this.onCancelGeneration,
  });

  @override
  Widget build(BuildContext context) {
    final isUser = message.isUser;
    final medicalTerm = isUser ? null : MedicalTerms.firstMatch(message.text);

    // Show the animated indicator while the assistant response is pending.
    if (message.isLoading) {
      return ThinkingBubble(
        showLongProcessingHint: showLongProcessingHint,
        onCancelGeneration: onCancelGeneration,
      );
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
                  backgroundColor: Color(0xFFE7F5F3),
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
                    color: isUser ? const Color(0xFF26A69A) : Colors.white,
                    borderRadius: BorderRadius.only(
                      topLeft: const Radius.circular(20),
                      topRight: const Radius.circular(20),
                      bottomLeft: Radius.circular(isUser ? 20 : 4),
                      bottomRight: Radius.circular(isUser ? 4 : 20),
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withValues(alpha: 0.05),
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
                          color: isUser
                              ? Colors.white
                              : const Color(0xFF2C5358),
                          fontSize: 15,
                        ),
                      ),
                      if (medicalTerm != null)
                        MedicalTermInfoBox(term: medicalTerm),
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