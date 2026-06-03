import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../../../core/widgets/responsive_frame.dart';
import '../../controllers/chat_controller.dart';
import '../../data/models/message_model.dart';
import '../../data/models/chat_response_model.dart';
import '../../utils/smart_replies.dart';
import '../../../warningscreen/presentation/screens/warning_page.dart';
import '../widgets/chat_app_bar.dart';
import '../widgets/chat_bubble.dart';
import '../widgets/chat_input_field.dart';
import '../widgets/latest_message_button.dart';
import '../../../../core/themes/theme_controller.dart';
import 'package:app1/core/services/speech_service.dart';

/// Main conversational UI for Careena.
///
/// This screen owns only presentation state such as input focus, scrolling,
/// smart replies, and delayed loading hints. Message data and backend work stay
/// inside [ChatController].
class ChatScreen extends StatefulWidget {
  /// Controller that provides message state and sends requests to the backend.
  final ChatController controller;

  /// Shared theme controller used to switch between light and dark mode.
  final ThemeController themeController;

  const ChatScreen({
    super.key,
    required this.controller,
    required this.themeController,
  });

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

/// Internal state for input handling, scrolling, and chat presentation effects.
class _ChatScreenState extends State<ChatScreen> {
  // Controllers and focus nodes are kept in state because they must survive
  // rebuilds and be disposed manually.
  final TextEditingController _textController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final FocusNode _inputFocusNode = FocusNode();
  final _speechService = SpeechService();

  // Local UI-only state. The chat messages themselves live in ChatController.
  List<String> _smartReplies = [];
  Timer? _longProcessingTimer;
  bool _isSending = false;
  bool _shouldAutoScroll = true;
  bool _showLongProcessingHint = false;
  bool _showLatestMessageButton = false;

  @override
  void initState() {
    super.initState();
    widget.controller.messages.addListener(_onMessagesChanged);
    
    widget.controller.init();
    _scrollController.addListener(_handleScrollChanged);
    widget.controller.messages.addListener(_handleMessagesChanged);

    // Wait for the first frame before requesting focus so Flutter has attached
    // the input field to the widget tree.
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;

      _inputFocusNode.requestFocus();
    });
  }

  Future<void> _handleSend() async {
    // Ignore double-submits while the current request is still in flight.
    if (_isSending) return;

    final text = _textController.text.trim();
    if (text.isEmpty) return;

    await _speechService.stop();

    // Clear input and smart replies immediately to make the UI feel responsive
    // before the network request starts.
    _textController.clear();
    setState(() {
      _isSending = true;
      _smartReplies = [];
      _showLongProcessingHint = false;
    });

    _longProcessingTimer?.cancel();
    // Only show the long-processing hint after a short delay so normal fast
    // responses do not create unnecessary visual noise.
    _longProcessingTimer = Timer(const Duration(seconds: 4), () {
      if (!mounted || !_isSending) return;

      setState(() => _showLongProcessingHint = true);
      _scrollToBottom();
    });

    // Start the backend call before scrolling so the optimistic user bubble and
    // loading bubble are already present when the scroll animation runs.
    final responseFuture = widget.controller.sendMessage(text);
    _scrollToBottom();

    ChatResponse? response;

    try {
      response = await responseFuture;
    } catch (_) {
      // The controller has already added a visible error bubble. Keeping the
      // response null prevents smart replies from being generated from failure.
      response = null;
    }

    _longProcessingTimer?.cancel();
    _scrollToBottom();

    if (!mounted) return;

    setState(() {
      _isSending = false;
      _showLongProcessingHint = false;
    });

    // Open the warning screen for red flag responses instead of showing a chat bubble.
    if (response?.redFlag == true) {
      Navigator.push(
        context,
        MaterialPageRoute(builder: (_) => WarningPage(response: response!)),
      );
      return;
    }

    _inputFocusNode.requestFocus();
  }


  void _onMessagesChanged() {
    // Get the current list of messages
    final messages = widget.controller.messages.value;

    if (messages.isEmpty) return;
    
    final lastMessage = messages.last;
    if (lastMessage.isLoading) return;
    if (lastMessage.isUser)  return;
    if (lastMessage.isStreaming) return;
    if (lastMessage.text.isEmpty) return;  
    
    // Generate smart replies from the latest assistant message
    setState(() {
      _smartReplies = SmartReplies.generate(lastMessage.text);
    });
  }

  /// Animates to the newest message after the current layout pass has finished.
  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted || !_scrollController.hasClients) return;

      if (_showLatestMessageButton) {
        // The button is no longer useful once the screen is returning to the
        // bottom automatically.
        setState(() => _showLatestMessageButton = false);
      }

      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    });
  }

  /// Jumps without animation for fast streaming updates.
  void _jumpToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted || !_scrollController.hasClients) return;

      _scrollController.jumpTo(_scrollController.position.maxScrollExtent);
    });
  }

  /// Supports keyboard navigation back to the beginning of the conversation.
  void _scrollToTop() {
    if (!_scrollController.hasClients) return;

    _scrollController.animateTo(
      _scrollController.position.minScrollExtent,
      duration: const Duration(milliseconds: 300),
      curve: Curves.easeOut,
    );
  }

  /// Returns focus to the input and resumes automatic scrolling.
  void _focusInputField() {
    _inputFocusNode.requestFocus();
    _shouldAutoScroll = true;
    _scrollToBottom();
  }

  /// Keeps the newest assistant text visible unless the user intentionally
  /// scrolled away from the bottom.
  void _handleMessagesChanged() {
    if (!_shouldAutoScroll && !_isSending) return;

    if (_isSending) {
      // Streaming updates can arrive very frequently. Jumping avoids stacking
      // many animations on top of each other while characters are appended.
      _jumpToBottom();
      return;
    }

    _scrollToBottom();
  }

  void _handleSmartReplySelected(String reply) {
    final currentText = _textController.text.trim();
    final newText = currentText.isEmpty ? reply : '$currentText $reply';

    _textController.text = newText;

    WidgetsBinding.instance.addPostFrameCallback((_) async {
      if (!mounted) return;

      _inputFocusNode.requestFocus();

      await Future.delayed(Duration.zero);

      _textController.selection = TextSelection.collapsed(
        offset: _textController.text.length,
      );
    });
  }

  /// Tracks whether the user is near the bottom and shows the jump button when
  /// new messages may otherwise arrive outside the visible area.
  void _handleScrollChanged() {
    final shouldShow = !_isNearBottom();

    _shouldAutoScroll = !shouldShow;

    if (shouldShow == _showLatestMessageButton) return;

    setState(() => _showLatestMessageButton = shouldShow);
  }

  /// Uses a small threshold so tiny scroll offsets do not disable auto-scroll.
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
    widget.controller.messages.removeListener(_onMessagesChanged);
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
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: ChatAppBar(
        onToggleTheme: widget.themeController.toggleTheme,
        isDarkMode: widget.themeController.isDarkMode,
      ),
      body: SafeArea(
        child: ResponsivePageBody(
          maxWidth: 820,
          child: Stack(
            children: [
              Column(
                children: [
                  Expanded(child: _buildMessageList()),
                  ChatInputField(
                    controller: _textController,
                    focusNode: _inputFocusNode,
                    isSending: _isSending,
                    onSend: _handleSend,
                    smartReplies: _smartReplies,
                    onSmartReplySelected: _handleSmartReplySelected,
                    speechService: _speechService,
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

  /// Builds the scrollable, keyboard-accessible message history.
  Widget _buildMessageList() {
    return FocusTraversalGroup(
      child: CallbackShortcuts(
        bindings: {
          // Desktop/web users can navigate the chat without reaching for a mouse.
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
                    // Loading messages have empty text, so screen readers need a
                    // meaningful label while the assistant response is pending.
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
