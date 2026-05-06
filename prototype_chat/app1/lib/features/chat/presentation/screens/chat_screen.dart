import 'package:app1/features/chat/presentation/themes/app_colors.dart';
import 'package:flutter/material.dart';
import '../chat_controller.dart';
import '../widgets/chat_bubble.dart';
import '../../../../../core/config/app_config.dart';

/// Main UI screen of the chat feature.
///
/// This screen is responsible for:
/// - Rendering the chat interface
/// - Displaying messages from the controller
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
/// Handles UI-specific responsibilities such as:
/// - Managing text input (TextEditingController)
/// - Controlling scroll behavior (ScrollController)
/// - Initializing the chat session on startup
/// - Triggering controller actions (send message, init)
/// - Managing widget life cycle (initState / dispose)
class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController textController = TextEditingController();
  final ScrollController scrollController = ScrollController();

  @override
  void initState() {
    super.initState();

    // Initialize chat session and load initial state
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      await widget.controller.init();
      _scrollToBottom();
    });
  }

  @override
  void dispose() {
    textController.dispose();
    scrollController.dispose();
    super.dispose();
  }

  /// Sends a message to the controller and clears the input field.
  ///
  /// Also ensures the chat view scrolls to the latest message.
  Future<void> send() async {
    final text = textController.text.trim();
    if (text.isEmpty) return;

    textController.clear();

    await widget.controller.sendMessage(text);
    _scrollToBottom();
  }

  /// Scrolls the chat list to the most recent message.
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
      backgroundColor: const Color(0xFFF6F7FB),

      /// Top App Bar
      appBar: AppBar(
        elevation: 0,
        backgroundColor: Colors.transparent,
        foregroundColor: Colors.black,
        title: const Text(
          AppConfig.appName,
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        centerTitle: true,
      ),

      body: Column(
        children: [
          /// Chat message list
          Expanded(
            child: ValueListenableBuilder(
              valueListenable: widget.controller.messages,
              builder: (context, messages, _) {
                WidgetsBinding.instance.addPostFrameCallback((_) {
                  _scrollToBottom();
                });

                return ListView.builder(
                  reverse: true,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 10,
                  ),
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

          /// Message input area
          Container(
            color: AppColors.lowerBarColor,
            padding: const EdgeInsets.symmetric(
              horizontal: 10,
              vertical: 8,
            ),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: textController,
                    onSubmitted: (_) => send(),
                    decoration: InputDecoration(
                      hintText: "Enter a message...",
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
                CircleAvatar(
                  backgroundColor: AppColors.primary,
                  child: IconButton(
                    icon: const Icon(Icons.send, color: Colors.white),
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