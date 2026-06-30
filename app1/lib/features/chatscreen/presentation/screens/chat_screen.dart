import 'package:app1/core/themes/app_colors.dart';
import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../../../core/widgets/careena_snack_bar.dart';
import '../../../../core/widgets/responsive_frame.dart';
import '../../controllers/chat_controller.dart';
import '../../controllers/chat_warning_controller.dart';
import '../../data/models/message_model.dart';
import '../../data/models/chat_response_model.dart';
import '../../utils/smart_replies.dart';
import '../../../warningscreen/presentation/screens/warning_page.dart';
import '../dialogs/leave_chat.dart';
import '../widgets/chat_app_bar.dart';
import '../widgets/chat_bubble.dart';
import '../widgets/chat_input_field.dart';
import '../widgets/chat_warning_dialog.dart';
import '../widgets/latest_message_button.dart';
import '../widgets/symptom_editor.dart';
import '../widgets/symptom_list.dart';
import '../../../../core/themes/theme_controller.dart';
import 'package:app1/core/services/speech_service.dart';
import 'package:app1/app/app_dependencies_scope.dart';

/// Main conversational UI for Careena.
///
/// This screen owns only presentation state such as input focus, scrolling,
/// smart replies, and delayed loading hints. Message data and backend work stay
/// inside [ChatController].
class ChatScreen extends StatefulWidget {
  final ChatController controller;
  final ThemeController themeController;
  final String leaveDialogMessage;
  final String leaveDialogConfirmLabel;

  const ChatScreen({
    super.key,
    required this.controller,
    required this.themeController,
    this.leaveDialogMessage =
        'Wenn du fortfährst, gelangst du zurück zur Startseite. '
        'Der aktuelle Chat wird nicht gespeichert.',
    this.leaveDialogConfirmLabel = 'Zur Startseite',
  });

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> with WidgetsBindingObserver {
  static const Duration _longProcessingHintDelay = Duration(seconds: 8);

  final TextEditingController _textController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  late final ChatWarningController _warningController;
  final FocusNode _inputFocusNode = FocusNode();
  final _speechService = SpeechService();

  List<String> _smartReplies = [];
  Timer? _longProcessingTimer;
  bool _isSending = false;
  bool _shouldAutoScroll = true;
  bool _showLongProcessingHint = false;
  bool _showLatestMessageButton = false;
  bool _allowPopAfterConfirmation = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    widget.controller.messages.addListener(_onMessagesChanged);

    unawaited(_initializeChat());
    _scrollController.addListener(_handleScrollChanged);
    widget.controller.messages.addListener(_handleMessagesChanged);

    // Wait for the first frame before requesting focus so Flutter has attached
    // the input field to the widget tree.
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      _warningController = AppDependenciesScope.of(
        context,
      ).chatWarningController;

      await _runWarningFlow();

      if (!mounted) return;

      _inputFocusNode.requestFocus();
    });
  }

  Future<void> _initializeChat() async {
    await widget.controller.init();
    if (!mounted) return;
    _onMessagesChanged();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed) {
      unawaited(widget.controller.refreshAvailability(refreshLlmStatus: true));
    }
  }

  Future<void> _runWarningFlow() async {
    final authSession = widget.controller.authSession;
    final activeProfile = authSession.activeProfile;
    final activeProfileId = activeProfile?.id;

    bool shouldShow = false;

    if (activeProfileId == null) {
      shouldShow = await _warningController.shouldShowWarning(null, null);
    } else {
      // Checks whether the warning has already been accepted by the user
      shouldShow = await _warningController.shouldShowWarning(
        activeProfileId,
        activeProfile?.aiDisclaimerAcceptedAt,
      );
    }

    if (!mounted || !shouldShow) return;

    // Shows a mandatory dialog that blocks interaction until confirmed
    final result = await showDialog(
      context: context,
      barrierDismissible: false,
      builder: (_) => const ChatWarningDialog(),
    );
    if (result == null) {
      if (!mounted) return;
      Navigator.of(context).pop();
      return;
    } // ChatScreen verlassen
    if (activeProfileId == null) {
      await _warningController.acceptWarning(null);
    } else {
      final acceptedAt = await _warningController.acceptWarning(
        activeProfileId,
      );
      if (acceptedAt != "") {
        authSession.setActiveProfileAiDisclaimerAcceptedAt(acceptedAt);
      }
    }
  }

  Future<void> _handleSend() async {
    if (_isSending) return;

    final text = _textController.text.trim();
    if (text.isEmpty) return;

    await _speechService.stop();
    _textController.clear();

    await _submitChatRequest(() => widget.controller.sendMessage(text));
  }

  Future<void> _handleRecommendationRequest() async {
    if (_isSending || widget.controller.isCompleted.value) return;

    await _speechService.stop();
    _textController.clear();

    _showRecommendationCheckHint();

    await _submitChatRequest(widget.controller.requestRecommendation);
  }

  Future<void> _submitChatRequest(
    Future<ChatResponse?> Function() request,
  ) async {
    setState(() {
      _isSending = true;
      _smartReplies = [];
      _showLongProcessingHint = false;
    });

    _longProcessingTimer?.cancel();
    _longProcessingTimer = Timer(_longProcessingHintDelay, () {
      if (!mounted || !_isSending) return;

      setState(() => _showLongProcessingHint = true);
      _scrollToBottom();
    });

    final responseFuture = request();
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
    });

    final showsRecommendation =
        response != null &&
        (widget.controller.chatService.isFinalRecommendation(response) ||
            widget.controller.chatService.isEmergencyRecommendation(response));

    final recommendationResponse = showsRecommendation ? response : null;

if (recommendationResponse != null) {
  final recommendationSessionId = widget.controller.currentSessionId;
  final recommendationAuthSession = widget.controller.authSession;

  final recommendationSymptoms = List<String>.from(
    widget.controller.symptoms.value,
  );
      final recommendationUserMessages = widget.controller.messages.value
          .where((message) => message.isUser)
          .map((message) => message.text.trim())
          .where((text) => text.isNotEmpty)
          .toList(growable: false);

      await widget.controller.resetChat();

      if (!mounted) return;

      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (_) => WarningPage(
            response: recommendationResponse,
            symptoms: recommendationSymptoms,
            userMessages: recommendationUserMessages,
            sessionId: recommendationSessionId,
            authSession: recommendationAuthSession,
          ),
        ),
      );
      return;
    }

    _inputFocusNode.requestFocus();
  }

  void _showRecommendationCheckHint() {
    showCareenaSnackBar(
      context,
      'Careena prüft jetzt, ob genug Angaben für eine Handlungsempfehlung vorliegen.',
    );
  }

  void _onMessagesChanged() {
    final messages = widget.controller.messages.value;

    if (messages.isEmpty) return;

    final lastMessage = messages.last;
    if (lastMessage.isLoading) return;
    if (lastMessage.isUser) return;
    if (lastMessage.isStreaming) return;
    if (lastMessage.text.isEmpty) return;

    // Use structured reply options from the backend when available (e.g. safety
    // clarification question), otherwise fall back to text-based generation.
    final backendOptions = widget.controller.lastReplyOptions.value;
    setState(() {
      _smartReplies = backendOptions.isNotEmpty
          ? backendOptions
          : SmartReplies.generate(lastMessage.text);
    });
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
    if (widget.controller.isCompleted.value) return;

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

  Future<void> _handleLeaveChat() async {
    if (widget.controller.authSession.isAuthenticated) {
      await _speechService.stop();
      if (!mounted) return;

      _allowPopAfterConfirmation = true;
      Navigator.of(context).pop();
      return;
    }

    final shouldLeave = await showLeaveChatDialog(
      context,
      message: widget.leaveDialogMessage,
      confirmLabel: widget.leaveDialogConfirmLabel,
    );

    if (!shouldLeave || !mounted) return;

    await _speechService.stop();
    await widget.controller.resetChat();

    if (!mounted) return;

    _allowPopAfterConfirmation = true;
    Navigator.of(context).pop();
  }

  Future<void> _showSymptomEditor() async {
    await showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      useSafeArea: true,
      builder: (context) {
        return SymptomEditor(
          symptoms: widget.controller.symptoms.value,
          onSave: widget.controller.updateSymptomsDirectly,
        );
      },
    );
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
    WidgetsBinding.instance.removeObserver(this);
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
    final backgroundColor = widget.themeController.isDarkMode
        ? Theme.of(context).scaffoldBackgroundColor
        : AppColors.chatBackgroundLight;

    return PopScope(
      canPop: _allowPopAfterConfirmation,
      onPopInvokedWithResult: (didPop, result) {
        if (didPop) return;

        _handleLeaveChat();
      },
      child: Scaffold(
        backgroundColor: backgroundColor,
        appBar: PreferredSize(
          preferredSize: const Size.fromHeight(kToolbarHeight),
          child: ValueListenableBuilder(
            valueListenable: widget.controller.availability,
            builder: (context, availability, _) {
              return ChatAppBar(
                onBackPressed: _handleLeaveChat,
                availability: availability,
              );
            },
          ),
        ),
        body: SafeArea(
          child: ResponsivePageBody(
            maxWidth: 820,
            child: Column(
              children: [
                Expanded(child: _buildMessageList()),
                ValueListenableBuilder(
                  valueListenable: widget.controller.isCompleted,
                  builder: (context, bool isCompleted, _) {
                    if (!isCompleted) {
                      return const SizedBox.shrink();
                    }

                    return const Padding(
                      padding: EdgeInsets.fromLTRB(12, 0, 12, 8),
                      child: _CompletedChatNotice(),
                    );
                  },
                ),
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      child: SymptomList(
                        symptomsListenable: widget.controller.symptoms,
                        onAddPressed: _showSymptomEditor,
                        onSymptomPressed: (_) => _showSymptomEditor(),
                      ),
                    ),
                    if (_showLatestMessageButton)
                      Padding(
                        padding: const EdgeInsets.only(
                          left: 8,
                          right: 12,
                          bottom: 8,
                        ),
                        child: LatestMessageButton(onPressed: _scrollToBottom),
                      ),
                  ],
                ),
                ValueListenableBuilder(
                  valueListenable: widget.controller.isCompleted,
                  builder: (context, bool isCompleted, _) {
                    if (isCompleted) {
                      return const SizedBox.shrink();
                    }

                    return ValueListenableBuilder(
                      valueListenable: widget.controller.messages,
                      builder: (context, List<Message> messages, _) {
                        return ValueListenableBuilder(
                          valueListenable: widget.controller.symptoms,
                          builder: (context, List<String> symptoms, _) {
                            if (!_hasRecommendationInput(messages, symptoms)) {
                              return const SizedBox.shrink();
                            }

                            return ValueListenableBuilder<Set<String>>(
                              valueListenable:
                                  widget.controller.continuingHistoryIds,
                              builder: (context, _, _) {
                                return Padding(
                                  padding: const EdgeInsets.fromLTRB(
                                    12,
                                    0,
                                    12,
                                    8,
                                  ),
                                  child: _RecommendationRequestButton(
                                    isEnabled:
                                        !_isSending &&
                                        !widget
                                            .controller
                                            .isActiveChatContinuing,
                                    onPressed: _handleRecommendationRequest,
                                  ),
                                );
                              },
                            );
                          },
                        );
                      },
                    );
                  },
                ),
                ValueListenableBuilder(
                  valueListenable: widget.controller.isCompleted,
                  builder: (context, bool isCompleted, _) {
                    return ValueListenableBuilder<Set<String>>(
                      valueListenable: widget.controller.continuingHistoryIds,
                      builder: (context, _, _) {
                        final isContinuing =
                            widget.controller.isActiveChatContinuing;

                        return ChatInputField(
                          controller: _textController,
                          focusNode: _inputFocusNode,
                          isSending: _isSending || isContinuing,
                          isEnabled: !isCompleted && !isContinuing,
                          onSend: _handleSend,
                          smartReplies: isCompleted || isContinuing
                              ? const []
                              : _smartReplies,
                          onSmartReplySelected: _handleSmartReplySelected,
                          speechService: _speechService,
                        );
                      },
                    );
                  },
                ),
              ],
            ),
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
                final userMessages = messages
                    .where((message) => message.isUser)
                    .map((message) => message.text.trim())
                    .where((text) => text.isNotEmpty)
                    .toList();
                return ListView.builder(
                  controller: _scrollController,
                  primary: false,
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
                            ? 'Deine Nachricht: $semanticText'
                            : 'Antwort von Careena: $semanticText',
                        child: ChatBubble(
                          authSession: widget.controller.authSession,
                          message: message,
                          symptoms: widget.controller.symptoms.value,
                          userMessages: userMessages,
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

  bool _hasRecommendationInput(List<Message> messages, List<String> symptoms) {
    // The backend still decides whether the available details are sufficient.
    return symptoms.isNotEmpty || messages.any((message) => message.isUser);
  }
}

class _RecommendationRequestButton extends StatelessWidget {
  final bool isEnabled;
  final VoidCallback onPressed;

  const _RecommendationRequestButton({
    required this.isEnabled,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      child: FilledButton.icon(
        onPressed: isEnabled ? onPressed : null,
        icon: const Icon(Icons.medical_information_outlined),
        label: const Text('Handlungsempfehlung anfordern'),
        style: FilledButton.styleFrom(
          backgroundColor: AppColors.careenaTeal,
          foregroundColor: AppColors.white,
          disabledBackgroundColor: AppColors.careenaTeal.withValues(
            alpha: 0.35,
          ),
          disabledForegroundColor: AppColors.white70,
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(14),
          ),
        ),
      ),
    );
  }
}

class _CompletedChatNotice extends StatelessWidget {
  const _CompletedChatNotice();

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        child: Text(
          'Dieser Chat wurde als Verlauf gespeichert. Du kannst die Empfehlung exportieren oder zur Startseite zurückgehen.',
          textAlign: TextAlign.center,
          style: TextStyle(
            color: Theme.of(context).colorScheme.onSurfaceVariant,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
    );
  }
}
