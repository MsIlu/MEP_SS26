import 'package:app1/features/chat/presentation/themes/app_colors.dart';
import 'package:flutter/material.dart';
import '../../controllers/chat_controller.dart';
import '../widgets/chat_bubble.dart';
import '../../utils/smart_replies.dart';

/// Chat screen (UI layer only)
///
/// Responsibility:
/// - Render chat UI
/// - Handle user input (text field, buttons)
/// - Listen to controller state (messages)
class ChatScreen extends StatefulWidget {
  final ChatController controller;

  const ChatScreen({
    super.key,
    required this.controller,
  });

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  /// Controls text input field
  final TextEditingController textController = TextEditingController();

  /// Focus node to automatically open keyboard
  final FocusNode _inputFocusNode = FocusNode();

  /// Controls list scrolling behavior
  final ScrollController scrollController = ScrollController();

  /// AI-generated quick reply suggestions
  List<String> smartReplies = [];

  @override
  void initState() {
    super.initState();

    /// Initialize chat session (important: backend + welcome message)
    widget.controller.init();

    /// Auto-focus input when screen opens
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _inputFocusNode.requestFocus();
    });
  }

  @override
  void dispose() {
    textController.dispose();
    scrollController.dispose();
    _inputFocusNode.dispose();
    super.dispose();
  }

  /// Sends user message to controller
  Future<void> send() async {
    final text = textController.text.trim();
    if (text.isEmpty) return;

    /// Clear quick replies when user sends new message
    setState(() {
      smartReplies = [];
    });

    /// Reset input field
    textController.clear();

    /// Delegate message handling to controller (clean architecture)
    await widget.controller.sendMessage(text);

    /// Scroll after message update
    _scrollToBottom();

    /// Generate smart replies based on last bot response
    Future.delayed(const Duration(milliseconds: 400), () {
      final messages = widget.controller.messages.value;

      if (messages.isNotEmpty && !messages.last.isUser) {
        setState(() {
          smartReplies =
              SmartReplies.generate(messages.last.text);
        });
      }
    });
  }

  /// Scrolls chat list to bottom
  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!scrollController.hasClients) return;

      scrollController.animateTo(
        scrollController.position.maxScrollExtent,
        duration: const Duration(milliseconds: 250),
        curve: Curves.easeOut,
      );
    });
  }

  /// Sends predefined quick reply
  void sendQuickReply(String text) {
    textController.text = text;
    send();
  }

  /// UI widget for quick reply chips
  Widget _quickReplyChip(String text) {
    return GestureDetector(
      onTap: () => sendQuickReply(text),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: AppColors.primary),
          color: AppColors.primary.withOpacity(0.05),
        ),
        child: Text(
          text,
          style: const TextStyle(
            color: AppColors.primary,
            fontSize: 13,
            fontWeight: FontWeight.w500,
          ),
        ),
      ),
    );
  }


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF6F7FB),

      /// Top bar showing bot status
      appBar: AppBar(
        elevation: 0,
        backgroundColor: Colors.white,
        centerTitle: true,
        title: Column(
          children: const [
            Text(
              "Careena",
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: Colors.black,
              ),
            ),
            SizedBox(height: 4),

            /// Online status indicator
            Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                CircleAvatar(
                  radius: 4,
                  backgroundColor: Colors.green,
                ),
                SizedBox(width: 6),
                Text(
                  "Online",
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),

      body: Column(
        children: [
          /// Chat message list
          Expanded(
            child: ValueListenableBuilder(
              valueListenable: widget.controller.messages,
              builder: (context, messages, _) {
                /// Auto-scroll when new messages arrive
                WidgetsBinding.instance.addPostFrameCallback((_) {
                  _scrollToBottom();
                });

                return ListView.builder(
                  controller: scrollController,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 10,
                  ),
                  itemCount: messages.length,
                  itemBuilder: (_, i) =>
                      ChatBubble(message: messages[i]),
                );
              },
            ),
          ),

          /// Quick replies section
          if (smartReplies.isNotEmpty)
            Padding(
              padding: const EdgeInsets.symmetric(
                horizontal: 12,
                vertical: 8,
              ),
              child: Wrap(
                spacing: 8,
                runSpacing: 8,
                children: smartReplies
                    .map((text) => _quickReplyChip(text))
                    .toList(),
              ),
            ),

          /// Input area
          Container(
            padding:
            const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
            decoration: BoxDecoration(
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.05),
                  blurRadius: 10,
                )
              ],
            ),
            child: Row(
              children: [
                /// Text input field
                Expanded(
                  child: TextField(
                    controller: textController,
                    focusNode: _inputFocusNode,
                    onSubmitted: (_) => send(),
                    decoration: InputDecoration(
                      hintText: "Nachricht eingeben...",
                      filled: true,
                      fillColor: AppColors.card,
                      contentPadding:
                      const EdgeInsets.symmetric(horizontal: 12),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(20),
                        borderSide: BorderSide.none,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 8),

                /// Send button
                Container(
                  decoration: const BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: LinearGradient(
                      colors: [
                        AppColors.primary,
                        Color(0xFF6C63FF)
                      ],
                    ),
                  ),
                  child: IconButton(
                    icon: const Icon(
                      Icons.arrow_upward_rounded,
                      color: Colors.white,
                    ),
                    onPressed: send,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}