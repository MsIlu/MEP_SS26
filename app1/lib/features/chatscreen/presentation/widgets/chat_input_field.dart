import 'package:flutter/material.dart';

class ChatInputField extends StatelessWidget {
  final TextEditingController controller;
  final VoidCallback onSend;
  final FocusNode focusNode;
  final bool isSending;

  const ChatInputField({
    super.key,
    required this.controller,
    required this.onSend,
    required this.focusNode,
    required this.isSending,
  });

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final isCompact = constraints.maxWidth < 360;

        return Container(
          padding: EdgeInsets.fromLTRB(
            isCompact ? 10 : 16,
            8,
            isCompact ? 10 : 16,
            16,
          ),
          decoration: const BoxDecoration(color: Colors.white),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Expanded(
                child: Semantics(
                  textField: true,
                  label: 'Eingabefeld für Symptome',
                  hint: 'Beschreiben Sie kurz Ihre Beschwerden.',
                  child: Container(
                    decoration: BoxDecoration(
                      color: const Color(0xFFF2F5FA),
                      borderRadius: BorderRadius.circular(25),
                    ),
                    child: Row(
                      children: [
                        SizedBox(width: isCompact ? 12 : 15),
                        Expanded(
                          child: TextField(
                            controller: controller,
                            focusNode: focusNode,
                            autofocus: true,
                            textInputAction: TextInputAction.send,
                            keyboardType: TextInputType.text,
                            minLines: 1,
                            maxLines: 4,
                            onSubmitted: (_) {
                              if (!isSending) {
                                onSend();
                              }
                            },
                            decoration: InputDecoration(
                              hintText: isCompact
                                  ? 'Beschwerden beschreiben'
                                  : 'Beschreiben Sie kurz Ihre Beschwerden',
                              border: InputBorder.none,
                            ),
                          ),
                        ),
                        if (!isCompact) ...[
                          const Icon(Icons.mic_none, color: Colors.grey),
                          const SizedBox(width: 15),
                        ] else
                          const SizedBox(width: 12),
                      ],
                    ),
                  ),
                ),
              ),
              SizedBox(width: isCompact ? 6 : 10),
              Semantics(
                button: true,
                enabled: !isSending,
                label: isSending
                    ? 'Nachricht wird verarbeitet'
                    : 'Symptombeschreibung senden',
                child: IconButton.filled(
                  onPressed: isSending ? null : onSend,
                  style: IconButton.styleFrom(
                    backgroundColor: const Color(0xFF26A69A),
                    disabledBackgroundColor: Colors.grey[300],
                    fixedSize: Size.square(isCompact ? 44 : 48),
                  ),
                  icon: Icon(
                    isSending ? Icons.hourglass_top : Icons.send,
                    color: Colors.white,
                    size: 20,
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}
