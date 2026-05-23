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
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
      decoration: const BoxDecoration(color: Colors.white),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Padding(padding: EdgeInsets.only(left: 4, bottom: 8)),
          Row(
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
                        const SizedBox(width: 15),
                        Expanded(
                          child: TextField(
                            controller: controller,
                            focusNode: focusNode,
                            autofocus: true,
                            textInputAction: TextInputAction.send,
                            keyboardType: TextInputType.text,
                            onSubmitted: (_) {
                              if (!isSending) {
                                onSend();
                              }
                            },
                            decoration: const InputDecoration(
                              hintText: 'Beschreiben Sie kurz Ihre Beschwerden',
                              border: InputBorder.none,
                            ),
                          ),
                        ),
                        const Icon(Icons.mic_none, color: Colors.grey),
                        const SizedBox(width: 15),
                      ],
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 10),
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
                    fixedSize: const Size.square(48),
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
        ],
      ),
    );
  }
}
