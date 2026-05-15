import 'package:flutter/material.dart';
import '../data/chat_api.dart';
import '../services/chat_service.dart';
import '../data/models/message_model.dart';
import '../../../core/config/app_config.dart';

class ChatController {
  final ChatApi chatApi;
  final ChatService chatService;

  ChatController({
    required this.chatApi,
    required this.chatService,
  });

  final ValueNotifier<List<Message>> messages =
  ValueNotifier<List<Message>>([]);

  String? _sessionId;

  Future<void> init() async {
    messages.value = [];

    _sessionId = await chatApi.createSession();

    chatService.addMessage(
      messages: messages,
      message: Message(
        text: AppConfig.welcomeMessage,
        isUser: false,
      ),
    );

    await chatApi.warmup();
  }

  Future<void> sendMessage(String text) async {
    if (_sessionId == null) {
      throw Exception("Chat session not initialized.");
    }

    final trimmed = text.trim();
    if (trimmed.isEmpty) return;

    chatService.addMessage(
      messages: messages,
      message: Message(
        text: trimmed,
        isUser: true,
      ),
    );

    chatService.addMessage(
      messages: messages,
      message: Message(
        text: '',
        isUser: false,
        isLoading: true,
      ),
    );

    try {
      final response =
      await chatApi.sendMessage(trimmed, _sessionId!);

      await chatService.streamResponse(
        messages: messages,
        fullText: response,
      );
    } catch (e) {
      chatService.removeLastBotMessage(messages);

      chatService.addMessage(
        messages: messages,
        message: Message(
          text: 'Fehler: $e',
          isUser: false,
        ),
      );
    }
  }
}