import 'package:flutter/material.dart';
import 'smart_reply_list.dart';
import '../themes/app_colors.dart';

/// Bottom input area for composing and sending chat messages.
class ChatInputField extends StatelessWidget {
  /// Text controller owned by the chat screen.
  final TextEditingController controller;

  /// Called when the user submits the current input.
  final VoidCallback onSend;

  /// Focus node used by the parent screen for keyboard navigation.
  final FocusNode focusNode;

  /// Disables submission while the previous message is still processing.
  final bool isSending;

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
  });

  @override
  Widget build(BuildContext context) {
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
          decoration: const BoxDecoration(
            color: Colors.white,
          ),
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
                          color: AppColors.background,
                          borderRadius: BorderRadius.circular(25),
                        ),
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            if (smartReplies.isNotEmpty)
                              Padding(
                                padding: const EdgeInsets.fromLTRB(
                                  12,
                                  4,
                                  12,
                                  6,
                                ),
                                child: SmartReplyList(
                                  replies: smartReplies,
                                  onSelected:onSmartReplySelected,)
                                ,
                              ),

                            Row(
                              crossAxisAlignment:
                                  CrossAxisAlignment.center,
                              children: [
                                SizedBox(width: isCompact ? 8 : 10,),

                                Expanded(
                                  child: TextField(
                                    controller: controller,
                                    focusNode: focusNode,
                                    autofocus: true,
                                    textInputAction:TextInputAction.send,
                                    keyboardType:TextInputType.text,
                                    minLines: 1,
                                    maxLines: 4,
                                    onSubmitted: (_) {
                                      // Pressing Enter should behave
                                      // like tapping send.
                                      if (!isSending) {
                                        onSend();
                                      }
                                    },
                                    decoration:
                                        InputDecoration(
                                      hintText: isCompact
                                          ? 'Beschwerden beschreiben'
                                          : 'Beschreiben Sie kurz Ihre Beschwerden',
                                      border:
                                          InputBorder.none,
                                    ),
                                  ),
                                ),

                                if (!isCompact) ...[
                                  const Tooltip(
                                    message:'Spracheingabe ist noch nicht verfügbar',
                                    child: Icon(Icons.mic_none,color: Colors.grey,),
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

                  SizedBox(width: isCompact ? 6 : 10,),
                  Semantics(
                    button: true,
                    enabled: !isSending,
                    label: isSending
                        ? 'Nachricht wird verarbeitet'
                        : 'Symptombeschreibung senden',
                    child: IconButton.filled(
                      onPressed:
                          isSending ? null : onSend,
                      style: IconButton.styleFrom(
                        backgroundColor:AppColors.careenaTeal,
                        disabledBackgroundColor:Colors.grey[300],
                        fixedSize: Size.square(isCompact ? 44 : 48,),
                      ),
                      icon: Icon(
                        isSending
                            ? Icons.hourglass_top
                            : Icons.send,
                        color: Colors.white,
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