import 'package:flutter/material.dart';
import 'smart_reply_list.dart';
import '../themes/app_colors.dart';
import 'package:app1/core/services/speech_service.dart';

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

  final SpeechService speechService;

  final List<String> smartReplies;
  final ValueChanged<String> onSmartReplySelected;

  const ChatInputField({
    super.key,
    required this.controller,
    required this.onSend,
    required this.focusNode,
    required this.isSending,
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

  // Pulsier-Animation für den Mic-Button während der Aufnahme
  late final AnimationController _pulseController = AnimationController(
    vsync: this,
    duration: const Duration(milliseconds: 900),
  );

  late final Animation<double> _pulseAnimation = Tween<double>(
    begin: 1.0,
    end: 1.3,
  ).animate(CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut));

  @override
void initState() {
  super.initState();

  widget.speechService.onListeningStopped = () {
    if (!mounted) return;

    _pulseController.stop();
    _pulseController.reset();

    setState(() => _isListening = false);
  };
}

  @override
  void dispose() {
    _pulseController.dispose();
    super.dispose();
  }

  // ── Spracheingabe ────────────────────────────────────────────────────────────

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
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text(
              'Mikrofon nicht verfügbar oder keine Berechtigung erteilt.',
            ),
            behavior: SnackBarBehavior.floating,
          ),
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
        // Erkannten Text live ins Eingabefeld schreiben
        widget.controller.text = text;
        widget.controller.selection = TextSelection.fromPosition(
          TextPosition(offset: text.length),
        );
      },
    );

    // Aufnahme automatisch beendet (Stille erkannt)
    //if (mounted) setState(() => _isListening = false);
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

    final outerBackground = isDarkMode ? const Color(0xFF1A2029) : Colors.white;

    final inputBackground = isDarkMode
        ? const Color(0xFF242B36)
        : AppColors.lightBackground;

    final sendButtonColor = isDarkMode
        ? const Color(0xFF3F8F87)
        : AppColors.careenaTeal;

    final sendingButtonColor = isDarkMode
        ? const Color(0xFF2F3A46)
        : AppColors.lightBackground;

    final sendingIconColor = isDarkMode
        ? colorScheme.onSurfaceVariant
        : AppColors.careenaMuted;

    return LayoutBuilder(
      builder: (context, constraints) {
        // The mic icon is hidden on compact widths to reserve enough room for
        // readable input text and the send button.
        // TODO: Implement mic logic
        final isCompact = constraints.maxWidth < 360;

        return Container(
          padding: EdgeInsets.fromLTRB(
            isCompact ? 10 : 16,
            8,
            isCompact ? 10 : 16,
            16,
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
                      hint: 'Beschreiben Sie kurz Ihre Beschwerden.',
                      child: Container(
                        decoration: BoxDecoration(
                          color: inputBackground,
                          borderRadius: BorderRadius.circular(25),
                        ),
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            if (widget.smartReplies.isNotEmpty)
                              Padding(
                                padding: const EdgeInsets.fromLTRB(
                                  12,
                                  4,
                                  12,
                                  6,
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
                                    textInputAction: TextInputAction.send,
                                    keyboardType: TextInputType.text,
                                    minLines: 1,
                                    maxLines: 4,
                                    style: TextStyle(
                                      color: colorScheme.onSurface,
                                      fontSize: 16,
                                    ),
                                    onSubmitted: (_) {
                                      // Pressing Enter should behave
                                      // like tapping send.
                                      if (!widget.isSending) {
                                        widget.onSend();
                                      }
                                    },
                                    decoration: InputDecoration(
                                      hintText: _isListening
                                          ? '🎤 Ich höre zu...'
                                          : (isCompact
                                                ? 'Beschwerden beschreiben'
                                                : 'Beschreiben Sie kurz Ihre Beschwerden'),
                                      hintStyle: TextStyle(
                                        color: colorScheme.onSurfaceVariant,
                                      ),
                                      border: InputBorder.none,
                                      enabledBorder: InputBorder.none,
                                      focusedBorder: InputBorder.none,
                                      filled: false,
                                      fillColor: Colors.transparent,
                                      isDense: true,
                                      contentPadding:
                                          const EdgeInsets.symmetric(
                                            vertical: 16,
                                          ),
                                    ),
                                  ),
                                ),

                                if (!isCompact) ...[
                                  Semantics(
                                    button: true,
                                    label: _isListening
                                        ? 'Sprachaufnahme stoppen'
                                        : 'Spracheingabe starten',

                                    child: GestureDetector(
                                      onTap: _toggleListening,

                                      child: AnimatedSwitcher(
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

                                            color: _isListening
                                                ? AppColors.careenaTeal
                                                : colorScheme.onSurfaceVariant,

                                            size: 22,
                                          ),
                                        ),
                                      ),
                                    ),
                                  ),

                                  const SizedBox(width: 15),
                                ] else
                                  const SizedBox(width: 12),
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
                    enabled: !widget.isSending,
                    label: widget.isSending
                        ? 'Nachricht wird verarbeitet'
                        : 'Symptombeschreibung senden',
                    child: IconButton.filled(
                      onPressed: widget.isSending ? null : widget.onSend,
                      style: IconButton.styleFrom(
                        backgroundColor: sendButtonColor,
                        disabledBackgroundColor: sendingButtonColor,
                        fixedSize: Size.square(isCompact ? 44 : 48),
                      ),
                      icon: Icon(
                        widget.isSending ? Icons.hourglass_top : Icons.send,
                        color: widget.isSending
                            ? sendingIconColor
                            : Colors.white,
                        size: 20,
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
