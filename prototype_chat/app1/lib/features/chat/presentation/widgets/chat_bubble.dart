import 'package:flutter/material.dart';
import '../../data/models/message_model.dart';
import 'thinking_bubble.dart';
import 'package:app1/features/chat/presentation/themes/app_colors.dart';

/// UI component that displays a single chat message.
///
/// This widget handles:
/// - Differentiating between user and assistant messages
/// - Rendering loading states (thinking indicator)
/// - Styling chat bubbles based on sender
class ChatBubble extends StatelessWidget {
  final Message message;

  const ChatBubble({super.key, required this.message});

  @override
  Widget build(BuildContext context) {
    final isUser = message.isUser;

    /// Show loading indicator when message is in "thinking" state
    if (message.isLoading) {
      return const ThinkingBubble();
    }

    return Align(
      alignment: isUser
          ? Alignment.centerRight
          : Alignment.centerLeft,

      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        margin: const EdgeInsets.symmetric(vertical: 6),
        padding: const EdgeInsets.symmetric(
          horizontal: 14,
          vertical: 10,
        ),
        constraints: const BoxConstraints(maxWidth: 300),

        decoration: BoxDecoration(
          /// Different bubble style depending on message sender
          color: isUser
              ? AppColors.primary
              : Colors.white,

          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(16),
            topRight: const Radius.circular(16),
            bottomLeft: Radius.circular(isUser ? 16 : 4),
            bottomRight: Radius.circular(isUser ? 4 : 16),
          ),

          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.06),
              blurRadius: 10,
              offset: const Offset(0, 4),
            )
          ],
        ),

        /// Message text content
        child: Text(
          message.text,
          style: TextStyle(
            color: isUser ? Colors.white : Colors.black87,
            fontSize: 15,
          ),
        ),
      ),
    );
  }
}