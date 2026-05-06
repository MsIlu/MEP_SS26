import 'package:app1/features/chat/presentation/themes/app_colors.dart';
import 'package:flutter/material.dart';
import '../chat_controller.dart';
import '../widgets/chat_bubble.dart';
import '../../../../../core/config/app_config.dart';

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
  final ScrollController scrollController = ScrollController();

  bool _initialized = false;

  @override
  void initState() {
    super.initState();

    if (!_initialized) {
      _initialized = true;

      widget.controller.init().then((_) {
        _scrollToBottom();
      });
    }
  }

  @override
  void dispose() {
    textController.dispose();
    scrollController.dispose();
    super.dispose();
  }

  Future<void> send() async {
    final text = textController.text.trim();
    if (text.isEmpty) return;

    textController.clear();

    await widget.controller.sendMessage(text);
    _scrollToBottom();
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF6F7FB),

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
          /// 💬 CHAT AREA
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
                    vertical: 12,
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

          /// ⌨️ INPUT BAR (Premium Style)
          SafeArea(
            child: Container(
              padding: const EdgeInsets.fromLTRB(12, 8, 12, 12),
              child: Row(
                children: [
                  /// Textfield
                  Expanded(
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 14),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(24),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.05),
                            blurRadius: 12,
                            offset: const Offset(0, 4),
                          )
                        ],
                      ),
                      child: TextField(
                        controller: textController,
                        onSubmitted: (_) => send(),
                        decoration: const InputDecoration(
                          hintText: "Nachricht eingeben...",
                          border: InputBorder.none,
                        ),
                      ),
                    ),
                  ),

                  const SizedBox(width: 10),

                  /// Send Button
                  GestureDetector(
                    onTap: send,
                    child: Container(
                      padding: const EdgeInsets.all(14),
                      decoration: const BoxDecoration(
                        color: Color(0xFF4F46E5),
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(
                        Icons.send,
                        color: Colors.white,
                        size: 18,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}