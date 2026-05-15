import 'package:flutter/material.dart';
import '../../controllers/chat_controller.dart';
import '../../data/models/message_model.dart';
import '../../utils/smart_replies.dart';
import '../widgets/chat_app_bar.dart';
import '../widgets/chat_bubble.dart';
import '../widgets/chat_input_field.dart';
import '../widgets/smart_reply_list.dart';

class ChatScreen extends StatefulWidget {
  final ChatController controller;
  const ChatScreen({super.key, required this.controller});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _textController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  List<String> _smartReplies = [];

  @override
  void initState() {
    super.initState();
    widget.controller.init();
  }

  void _handleSend() async {
    final text = _textController.text.trim();
    if (text.isEmpty) return;

    _textController.clear();
    setState(() => _smartReplies = []);

    final response = await widget.controller.sendMessage(text);
    _scrollToBottom();

    if (!mounted || response == null) return;

    setState(() => _smartReplies = SmartReplies.generate(response.text));
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!_scrollController.hasClients) return;

      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    });
  }

  void _handleSmartReplySelected(String reply) {
    _textController.text = reply;
    _handleSend();
  }

  @override
  void dispose() {
    _textController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF2F5FA),
      appBar: const ChatAppBar(),
      body: Column(
        children: [
          Expanded(child: _buildMessageList()),
          SmartReplyList(
            replies: _smartReplies,
            onSelected: _handleSmartReplySelected,
          ),
          ChatInputField(controller: _textController, onSend: _handleSend),
        ],
      ),
    );
  }

  Widget _buildMessageList() {
    return ValueListenableBuilder(
      valueListenable: widget.controller.messages,
      builder: (context, List<Message> messages, _) {
        return ListView.builder(
          controller: _scrollController,
          padding: const EdgeInsets.symmetric(vertical: 10),
          itemCount: messages.length,
          itemBuilder: (context, index) => ChatBubble(message: messages[index]),
        );
      },
    );
  }
}
