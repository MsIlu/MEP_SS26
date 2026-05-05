import 'package:app1/features/chat/presentation/themes/app_colors.dart';
import 'package:flutter/material.dart';
import 'chat_controller.dart';
import 'widgets/chat_bubble.dart';
import '../../../../core/config/app_config.dart';

/// Main UI screen of the chat feature.
///
/// Responsible for:
/// - Rendering the chat interface
/// - Handling user input
/// - Connecting UI events to the ChatController
class ChatScreen extends StatefulWidget {
  final ChatController controller;

  const ChatScreen({
    super.key,
    required this.controller,
  });

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

/// Internal state of the ChatScreen widget.
///
/// Handles UI-only concerns such as:
/// - Text input management (TextEditingController)
/// - Scroll behavior (ScrollController)
/// - Session-ID für den Chat-Verlauf
/// - Widget lifecycle (initState / dispose)
/// - Triggern von Controller-Aktionen beim Start und beim Senden von Nachrichten

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController textController = TextEditingController();
  final ScrollController scrollController = ScrollController();

  @override
  void initState() {
    super.initState();

    // Initialize chat session (API + welcome message)
    widget.controller.init().then((_) {
      _scrollToBottom();
    });
  }

  @override
  void dispose() {
    textController.dispose();
    scrollController.dispose();
    super.dispose();
  }

  /// Sends a message to the controller and resets the input field.
  /// Also triggers auto-scrol to the newest message.
  Future<void> send() async {
    final text = textController.text.trim();
    if (text.isEmpty) return;

    textController.clear();

    await widget.controller.sendMessage(text);
    _scrollToBottom();
  }

  /// Scrolls the chat list to the latest message.
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // Top App Bar
      appBar: AppBar(
        title: const Text(AppConfig.appName),
        backgroundColor: AppColors.upperBarColor,
      ),
      body: Column(
        children: [
          /// Chat message list
          Expanded(
            child: ValueListenableBuilder(
              valueListenable: widget.controller.messages,
              builder: (context, messages, _) {
                return ListView.builder(
                  reverse: true,
                  controller: scrollController,
                  itemCount: messages.length,
                  itemBuilder: (_, i) {
                    final msg = messages[messages.length - 1 - i];
                    return ChatBubble(message: msg);
                  },
                );
              },
            ),
          ),

          /// Input area
          Container(
            color: AppColors.lowerBarColor,
            padding: const EdgeInsets.symmetric(
              horizontal: 8,
              vertical: 6,
            ),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: textController,
                    onSubmitted: (_) => send(),
                    decoration: const InputDecoration(
                      hintText: "Nachricht eingeben...",
                      border: InputBorder.none,
                    ),
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.send),
                  onPressed: send,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}