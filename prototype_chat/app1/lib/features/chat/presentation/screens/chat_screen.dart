import 'package:app1/features/chat/presentation/themes/app_colors.dart';
import 'package:flutter/material.dart';
import '../../controllers/chat_controller.dart';
import '../widgets/chat_bubble.dart';
import '../../utils/smart_replies.dart';

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

  List<String> smartReplies = [];

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

    // remove old chips immediately
    setState(() {
      smartReplies = [];
    });

    textController.clear();

    await widget.controller.sendMessage(text);
    _scrollToBottom();

    // Wait for answer to be done
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

  /// Scrolls the chat list to the most recent message.
  void _scrollToBottom() {
    if (!scrollController.hasClients) return;

    final position = scrollController.position.maxScrollExtent;

    scrollController.animateTo(
      position,
      duration: const Duration(milliseconds: 250),
      curve: Curves.easeOut,
    );
  }

  void sendQuickReply(String text) {
    setState(() {
      smartReplies = [];
    });

    textController.text = text;
    send();
  }

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

      /// Top App Bar
      appBar: AppBar(
        elevation: 0,
        backgroundColor: Colors.white,
        centerTitle: true,
        title: Column(
          children: [
          const Text(
          "Careena (Bot)",
          style: TextStyle(
            fontWeight: FontWeight.bold,
            color: Colors.black,
          ),
        ),
          Row(
            mainAxisSize: MainAxisSize.min,
            children: const [
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
                WidgetsBinding.instance.addPostFrameCallback((_) {
                  _scrollToBottom();
                });

                return Column(
                  children: [
                    Expanded(
                      child: ListView.builder(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 10,
                        ),
                        controller: scrollController,
                        itemCount: messages.length,
                        itemBuilder: (_, i) => ChatBubble(message: messages[i]),
                      ),
                    ),

                    /// Quick replies appear only with bot
                    AnimatedSwitcher(
                      duration: const Duration(milliseconds: 250),
                      child: smartReplies.isNotEmpty
                          ? Padding(
                        key: ValueKey(smartReplies.join()),
                        padding: const EdgeInsets.symmetric(
                            horizontal: 12, vertical: 8),
                        child: Wrap(
                          spacing: 8,
                          runSpacing: 8,
                          children: smartReplies
                              .map((text) => _quickReplyChip(text))
                              .toList(),
                        ),
                      )
                          : const SizedBox(),
                    ),
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                        child: Wrap(
                          spacing: 8,
                          runSpacing: 8,
                          children: smartReplies
                              .map((text) => _quickReplyChip(text))
                              .toList(),
                        ),
                      ),
                  ],
                );
              },
            ),
          ),

          /// Message input area
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
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
                Expanded(
                  child: TextField(
                    controller: textController,
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
                Container(
                  decoration: const BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: LinearGradient(
                      colors: [AppColors.primary, Color(0xFF6C63FF)],
                    ),
                  ),
                  child: IconButton(
                    icon: const Icon(Icons.arrow_upward_rounded, color: Colors.white),
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