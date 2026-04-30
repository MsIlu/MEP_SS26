import 'package:app1/core/config/app_config.dart';
import 'package:app1/features/chat/data/chat_api.dart';
import 'package:flutter/material.dart';
import '../data/models/message_model.dart';

/// Zentrale Logik für Chat State Management.
///
/// Steuert Nachrichtenfluss, API Kommunikation und UI Updates.
/// 
/// DEV NOTE:
/// **ValueNotifier bei messages könnte problematico werden
/// **Doppeltes State Handling
/// 
/// ** lieber nicht anfassen wenn ihr euch nicht sicher seid
class ChatController {
  final ChatApi chatApi;

  ChatController(this.chatApi);

  final messages = ValueNotifier<List<Message>>([]);

  Future<void> sendMessage(String text, String sessionId) async {
    if (text.trim().isEmpty) return;

    final current = [...messages.value];

    current.add(Message(text: text, isUser: true));
    messages.value = current;

    try {
      final reply = await chatApi.sendMessage(text, sessionId);

      messages.value = [
        ...messages.value,
        Message(text: reply, isUser: false),
      ];
    } catch (e) {
      messages.value = [
        ...messages.value,
        Message(text: "Fehler: $e", isUser: false),
      ];
    }
  }

  Future<void> warmup() {
    return chatApi.warmup();
  }

  void addWelcomeMessage() {
    messages.value = [
        Message(
          text: AppConfig.welcomeMessage,
          isUser: false,
        ),
    ];
}

}