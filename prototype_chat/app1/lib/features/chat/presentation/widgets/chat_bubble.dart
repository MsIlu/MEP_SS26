import 'package:flutter/material.dart';
import '../../data/models/message_model.dart';

class ChatBubble extends StatelessWidget {
  final Message message;

  const ChatBubble({super.key, required this.message});

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: message.isUser
          ? Alignment.centerRight
          : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(
          vertical: 4,
          horizontal: 8,
        ),
        padding: const EdgeInsets.all(12),
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.7,
        ),
        decoration: BoxDecoration(
          color: message.isUser
              ? Colors.blue
              : Colors.grey[300],
          borderRadius: BorderRadius.circular(12),
        ),
        child: Text(
          message.text,
          style: TextStyle(
            color: message.isUser
                ? Colors.white
                : Colors.black,
          ),
        ),
      ),
    );
  }
}