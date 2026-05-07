import 'package:app1/features/chat/presentation/themes/app_colors.dart';
import 'package:flutter/material.dart';
import '../../controllers/chat_controller.dart';
import '../widgets/chat_bubble.dart';
import '../../utils/smart_replies.dart';

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
  final TextEditingController textController = TextEditingController();
  final FocusNode _inputFocusNode = FocusNode();
  final ScrollController scrollController = ScrollController();

  List<String> smartReplies = [];

  @override
  void initState() {
    super.initState();

    widget.controller.init();

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

  Future<void> send() async {
    final text = textController.text.trim();
    if (text.isEmpty) return;

    setState(() {
      smartReplies = [];
    });

    textController.clear();

    await widget.controller.sendMessage(text);

    _scrollToBottom();

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

  void sendQuickReply(String text) {
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

      appBar: AppBar(
        elevation: 0,
        backgroundColor: Colors.white,
        centerTitle: true,
        title: Column(
          children: const [
            Text(
              "Careena (Bot)",
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: Colors.black,
              ),
            ),
            SizedBox(height: 4),
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
          /// CHAT LIST
          Expanded(
            child: ValueListenableBuilder(
              valueListenable: widget.controller.messages,
              builder: (context, messages, _) {
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

          /// QUICK REPLIES (ONLY ONCE, FIXED)
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

          /// INPUT
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