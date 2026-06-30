import 'package:flutter/material.dart';
import 'smart_reply_list.dart';
import 'package:app1/core/themes/app_colors.dart';
import 'package:app1/core/services/speech_service.dart';
import '../../../../core/widgets/careena_snack_bar.dart';

/// Bottom input area for composing and sending chat messages.
class ChatInputField extends StatefulWidget {
  /// Text controller owned by the chat screen.
  final TextEditingController controller;

  /// Called when the user submits the current input.
  final VoidCallback onSend;

  /// Focus node used by the parent screen for keyboard navigation.
  final FocusNode focusNode;

  /// Disables submission while the previous message is still processing.
  final bool isSending;
  final bool isEnabled;

  final SpeechService speechService;

  final List<String> smartReplies;
  final ValueChanged<String> onSmartReplySelected;

  /// When true the text field is locked and the user must answer via a
  /// smart-reply bubble (e.g. during a safety clarification question).
  final bool lockedToReplies;

  const ChatInputField({
    super.key,
    required this.controller,
    required this.onSend,
    required this.focusNode,
    required this.isSending,
    this.isEnabled = true,
    this.lockedToReplies = false,
    required this.smartReplies,
    required this.onSmartReplySelected,
    required this.speechService,
  });

  @override
  State<ChatInputField> createState() => _ChatInputFieldState();
}

class _ChatInputFieldState extends State<ChatInputField>
    with SingleTickerProviderStateMixin {
  bool _isListening = false;

  late final AnimationController _pulseController;

  late final Animation<double> _pulseAnimation;

  @override
  void initState() {
    super.initState();

    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 900),
    );

    _pulseAnimation = Tween<double>(begin: 1.0, end: 1.3).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );

    widget.speechService.onListeningStopped = () {
      if (!mounted) return;

      _pulseController.stop();
      _pulseController.reset();

      setState(() => _isListening = false);
    };
  }

  @override
  void dispose() {
    widget.speechService.onListeningStopped = null;
    _pulseController.dispose();
    super.dispose();
  }

  Future<void> _toggleListening() async {
    if (_isListening) {
      await _stopListening();
    } else {
      await _startListening();
    }
  }

  Future<void> _startListening() async {
    final available = await widget.speechService.initialize();

    if (!available) {
      if (mounted) {
        showCareenaSnackBar(
          context,
          'Mikrofon nicht verfügbar oder keine Berechtigung erteilt.',
        );
      }
      return;
    }

    await widget.speechService.stop();

    widget.controller.clear();

    setState(() => _isListening = true);

    _pulseController.repeat(reverse: true);

    await widget.speechService.listen(
      onResult: (text) {
        if (!widget.speechService.isListening) return;

        // Mirror recognized speech into the input field while recording.
        widget.controller.text = text;
        widget.controller.selection = TextSelection.fromPosition(
          TextPosition(offset: text.length),
        );
      },
    );

    // Recording completion is reported through onListeningStopped.
    // Keeping that state transition in one callback avoids duplicate updates.
  }

  Future<void> _stopListening() async {
    await widget.speechService.stop();
    _pulseController.stop();
    _pulseController.reset();
    if (mounted) setState(() => _isListening = false);
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    final outerBackground = isDarkMode
        ? AppColors.chatInputOuterDark
        : AppColors.white;

    final inputBackground = isDarkMode
        ? AppColors.chatInputInnerDark
        : AppColors.lightBackground;

    final sendButtonColor = isDarkMode
        ? AppColors.chatInputAccentDark
        : AppColors.careenaTeal;

    final sendingButtonColor = isDarkMode
        ? AppColors.chatInputDisabledDark
        : AppColors.lightBackground;

    final sendingIconColor = isDarkMode
        ? colorScheme.onSurfaceVariant
        : AppColors.careenaMuted;
    final accentForeground = isDarkMode
        ? AppColors.careenaAccentOnDark
        : AppColors.careenaTeal;

    return LayoutBuilder(
      builder: (context, constraints) {
        final isShortViewport = MediaQuery.sizeOf(context).height < 520;
        final isCompact = constraints.maxWidth < 420 || isShortViewport;
        final horizontalPadding = isCompact ? 10.0 : 16.0;
        final topPadding = isShortViewport ? 4.0 : 8.0;
        final bottomPadding = isShortViewport ? 8.0 : 16.0;
        final fieldVerticalPadding = isShortViewport ? 10.0 : 16.0;
        final buttonSize = isShortViewport ? 40.0 : (isCompact ? 44.0 : 48.0);
        final isInputEnabled =
            widget.isEnabled && !widget.isSending && !widget.lockedToReplies;
        final canUseMic = widget.isEnabled && !widget.lockedToReplies;
        final micButtonSize = isShortViewport ? 36.0 : 40.0;
        final micIconColor = !canUseMic
            ? colorScheme.onSurfaceVariant.withValues(alpha: 0.38)
            : (_isListening ? accentForeground : colorScheme.onSurfaceVariant);
        final sendButtonLabel = widget.isSending
            ? 'Nachricht wird verarbeitet'
            : !widget.isEnabled
            ? 'Chat ist abgeschlossen'
            : 'Nachricht senden';

        return Container(
          padding: EdgeInsets.fromLTRB(
            horizontalPadding,
            topPadding,
            horizontalPadding,
            bottomPadding,
          ),
          decoration: BoxDecoration(color: outerBackground),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Expanded(
                    child: Semantics(
                      textField: true,
                      label: 'Eingabefeld für Symptome',
                      hint: 'Beschreibe kurz deine Beschwerden.',
                      child: Container(
                        clipBehavior: Clip.antiAlias,
                        decoration: BoxDecoration(
                          color: inputBackground,
                          borderRadius: BorderRadius.circular(
                            isShortViewport ? 20 : 25,
                          ),
                          border: Border.all(
                            color: AppColors.careenaTeal.withValues(
                              alpha: 0.25,
                            ),
                            width: 1,
                          ),
                          boxShadow: [
                            BoxShadow(
                              color: AppColors.black.withValues(alpha: 0.08),
                              blurRadius: 12,
                              offset: const Offset(0, 4),
                            ),
                          ],
                        ),
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            if (widget.isEnabled &&
                                widget.smartReplies.isNotEmpty)
                              Padding(
                                padding: EdgeInsets.fromLTRB(
                                  isShortViewport ? 8 : 12,
                                  isShortViewport ? 2 : 4,
                                  isShortViewport ? 8 : 12,
                                  isShortViewport ? 2 : 6,
                                ),
                                child: SmartReplyList(
                                  replies: widget.smartReplies,
                                  onSelected: widget.onSmartReplySelected,
                                ),
                              ),

                            Row(
                              crossAxisAlignment: CrossAxisAlignment.center,
                              children: [
                                SizedBox(width: isCompact ? 8 : 10),

                                Expanded(
                                  child: TextField(
                                    controller: widget.controller,
                                    focusNode: widget.focusNode,
                                    autofocus: true,
                                    enabled:
                                        widget.isEnabled &&
                                        !widget.lockedToReplies,
                                    textInputAction: TextInputAction.send,
                                    keyboardType: TextInputType.text,
                                    minLines: 1,
                                    maxLines: isShortViewport ? 2 : 4,
                                    style: TextStyle(
                                      color: colorScheme.onSurface,
                                      fontSize: isShortViewport ? 15 : 16,
                                    ),
                                    onSubmitted: (_) {
                                      // Pressing Enter should behave
                                      // like tapping send.
                                      if (isInputEnabled) {
                                        widget.onSend();
                                      }
                                    },
                                    decoration: InputDecoration(
                                      hintText: _isListening
                                          ? 'Ich höre zu...'
                                          : (!widget.isEnabled
                                                ? 'Chat abgeschlossen'
                                                : (widget.lockedToReplies
                                                      ? 'Bitte eine Antwort auswählen'
                                                      : (isCompact
                                                            ? 'Beschwerden beschreiben'
                                                            : 'Beschreibe kurz deine Beschwerden'))),
                                      hintStyle: TextStyle(
                                        color: colorScheme.onSurfaceVariant,
                                      ),
                                      border: InputBorder.none,
                                      enabledBorder: InputBorder.none,
                                      focusedBorder: InputBorder.none,
                                      filled: false,
                                      fillColor: AppColors.transparent,
                                      isDense: true,
                                      contentPadding: EdgeInsets.symmetric(
                                        vertical: fieldVerticalPadding,
                                      ),
                                    ),
                                  ),
                                ),

                                Semantics(
                                  button: true,
                                  enabled: canUseMic,
                                  label: _isListening
                                      ? 'Sprachaufnahme stoppen'
                                      : 'Spracheingabe starten',
                                  child: SizedBox.square(
                                    dimension: micButtonSize,
                                    child: IconButton(
                                      tooltip: _isListening
                                          ? 'Sprachaufnahme stoppen'
                                          : 'Spracheingabe starten',
                                      onPressed: canUseMic
                                          ? _toggleListening
                                          : null,
                                      padding: EdgeInsets.zero,
                                      visualDensity: VisualDensity.compact,
                                      style: IconButton.styleFrom(
                                        tapTargetSize:
                                            MaterialTapTargetSize.shrinkWrap,
                                        minimumSize: Size.square(micButtonSize),
                                      ),
                                      icon: AnimatedSwitcher(
                                        duration: const Duration(
                                          milliseconds: 200,
                                        ),
                                        child: ScaleTransition(
                                          scale: _isListening
                                              ? _pulseAnimation
                                              : const AlwaysStoppedAnimation(
                                                  1.0,
                                                ),
                                          child: Icon(
                                            _isListening
                                                ? Icons.mic
                                                : Icons.mic_none,
                                            key: ValueKey(_isListening),
                                            color: micIconColor,
                                            size: 22,
                                          ),
                                        ),
                                      ),
                                    ),
                                  ),
                                ),

                                SizedBox(width: isCompact ? 4 : 10),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),

                  SizedBox(width: isCompact ? 6 : 10),
                  Semantics(
                    button: true,
                    enabled: isInputEnabled,
                    label: sendButtonLabel,
                    onTap: isInputEnabled ? widget.onSend : null,
                    child: ExcludeSemantics(
                      child: IconButton.filled(
                        tooltip: sendButtonLabel,
                        onPressed: isInputEnabled ? widget.onSend : null,
                        style: IconButton.styleFrom(
                          backgroundColor: sendButtonColor,
                          disabledBackgroundColor: sendingButtonColor,
                          fixedSize: Size.square(buttonSize),
                        ),
                        icon: Icon(
                          widget.isSending ? Icons.hourglass_top : Icons.send,
                          color: isInputEnabled
                              ? AppColors.white
                              : sendingIconColor,
                          size: 20,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        );
      },
    );
  }
}
