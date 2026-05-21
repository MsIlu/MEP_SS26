import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../../../core/widgets/responsive_frame.dart';
import '../../controllers/chat_controller.dart';
import '../../data/models/message_model.dart';
import '../../data/models/chat_response_model.dart';
import '../../utils/smart_replies.dart';
import '../../../warning/presentation/screens/warning_page.dart';
import '../widgets/chat_app_bar.dart';
import '../widgets/chat_bubble.dart';
import '../widgets/chat_input_field.dart';
import '../widgets/latest_message_button.dart';
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
  final FocusNode _inputFocusNode = FocusNode();

  List<String> _smartReplies = [];
  Timer? _longProcessingTimer;
  bool _isSending = false;
  bool _shouldAutoScroll = true;
  bool _showLongProcessingHint = false;
  bool _showLatestMessageButton = false;

  @override
  void initState() {
    super.initState();
    widget.controller.init();
    _scrollController.addListener(_handleScrollChanged);
    widget.controller.messages.addListener(_handleMessagesChanged);

    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;

      _inputFocusNode.requestFocus();
    });
  }

  Future<void> _handleSend() async {
    if (_isSending) return;

    final text = _textController.text.trim();
    if (text.isEmpty) return;

    _textController.clear();
    setState(() {
      _isSending = true;
      _smartReplies = [];
      _showLongProcessingHint = false;
    });

    _longProcessingTimer?.cancel();
    _longProcessingTimer = Timer(const Duration(seconds: 4), () {
      if (!mounted || !_isSending) return;

      setState(() => _showLongProcessingHint = true);
      _scrollToBottom();
    });

    final responseFuture = widget.controller.sendMessage(text);
    _scrollToBottom();

    ChatResponse? response;

    try {
      response = await responseFuture;
    } catch (_) {
      response = null;
    }

    _longProcessingTimer?.cancel();
    _scrollToBottom();

    if (!mounted) return;

    setState(() {
      _isSending = false;
      _showLongProcessingHint = false;
      _smartReplies = [];
    });

    // Open the warning page for red flag responses instead of showing a chat bubble.
    if (response?.redFlag == true) {
      Navigator.push(
        context,
        MaterialPageRoute(builder: (_) => WarningPage(response: response!)),
      );
      return;
    }

    setState(() {
      _smartReplies = response == null
          ? []
          : SmartReplies.generate(response.text);
    });

    _inputFocusNode.requestFocus();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted || !_scrollController.hasClients) return;

      if (_showLatestMessageButton) {
        setState(() => _showLatestMessageButton = false);
      }

      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    });
  }

  void _jumpToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted || !_scrollController.hasClients) return;

      _scrollController.jumpTo(_scrollController.position.maxScrollExtent);
    });
  }

  void _scrollToTop() {
    if (!_scrollController.hasClients) return;

    _scrollController.animateTo(
      _scrollController.position.minScrollExtent,
      duration: const Duration(milliseconds: 300),
      curve: Curves.easeOut,
    );
  }

  void _focusInputField() {
    _inputFocusNode.requestFocus();
    _shouldAutoScroll = true;
    _scrollToBottom();
  }

  void _handleMessagesChanged() {
    if (!_shouldAutoScroll && !_isSending) return;

    if (_isSending) {
      _jumpToBottom();
      return;
    }

    _scrollToBottom();
  }

  void _handleSmartReplySelected(String reply) {
    _textController.text = reply;
    _handleSend();
  }

  void _handleScrollChanged() {
    final shouldShow = !_isNearBottom();

    _shouldAutoScroll = !shouldShow;

    if (shouldShow == _showLatestMessageButton) return;

    setState(() => _showLatestMessageButton = shouldShow);
  }

  bool _isNearBottom() {
    if (!_scrollController.hasClients) {
      return true;
    }

    final distanceFromBottom =
        _scrollController.position.maxScrollExtent - _scrollController.offset;

    return distanceFromBottom < 80;
  }

  @override
  void dispose() {
    _longProcessingTimer?.cancel();
    widget.controller.messages.removeListener(_handleMessagesChanged);
    _scrollController.removeListener(_handleScrollChanged);
    _textController.dispose();
    _scrollController.dispose();
    _inputFocusNode.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF2F5FA),
      appBar: const ChatAppBar(),
      body: SafeArea(
        child: ResponsivePageBody(
          maxWidth: 820,
          child: Stack(
            children: [
              Column(
                children: [
                  Expanded(child: _buildMessageList()),
                  SmartReplyList(
                    replies: _smartReplies,
                    onSelected: _handleSmartReplySelected,
                  ),
                  ChatInputField(
                    controller: _textController,
                    focusNode: _inputFocusNode,
                    isSending: _isSending,
                    onSend: _handleSend,
                  ),
                ],
              ),
              if (_showLatestMessageButton)
                Positioned(
                  right: 16,
                  bottom: 132,
                  child: LatestMessageButton(onPressed: _scrollToBottom),
                ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildMessageList() {
    return FocusTraversalGroup(
      child: CallbackShortcuts(
        bindings: {
          const SingleActivator(LogicalKeyboardKey.end): _scrollToBottom,
          const SingleActivator(LogicalKeyboardKey.home): _scrollToTop,
          const SingleActivator(LogicalKeyboardKey.arrowDown): _focusInputField,
          const SingleActivator(LogicalKeyboardKey.arrowRight):
              _focusInputField,
        },
        child: Focus(
          child: Scrollbar(
            controller: _scrollController,
            thumbVisibility: true,
            child: ValueListenableBuilder(
              valueListenable: widget.controller.messages,
              builder: (context, List<Message> messages, _) {
                return ListView.builder(
                  controller: _scrollController,
                  keyboardDismissBehavior:
                      ScrollViewKeyboardDismissBehavior.onDrag,
                  padding: const EdgeInsets.symmetric(vertical: 10),
                  itemCount: messages.length,
                  itemBuilder: (context, index) {
                    final message = messages[index];
                    final semanticText = message.isLoading
                        ? 'Careena schreibt...'
                        : message.text;

                    return Focus(
                      canRequestFocus: true,
                      child: Semantics(
                        label: message.isUser
                            ? 'Ihre Nachricht: $semanticText'
                            : 'Antwort von Careena: $semanticText',
                        child: ChatBubble(
                          message: message,
                          showLongProcessingHint:
                              message.isLoading && _showLongProcessingHint,
                        ),
                      ),
                    );
                  },
                );
              },
            ),
          ),
        ),
      ),
    );
  }
}
