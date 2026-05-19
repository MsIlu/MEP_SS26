import 'package:flutter/material.dart';
import '../../../core/config/app_config.dart';
import '../data/chat_api.dart';
import '../data/models/message_model.dart';
import '../services/chat_service.dart';

class ChatController {
  final ChatApi chatApi;
  final ChatService chatService;

  ChatController({required this.chatApi, required this.chatService});

  final ValueNotifier<List<Message>> messages = ValueNotifier<List<Message>>(
    [],
  );

  String? _sessionId;

  Future<void> init() async {
    _setMessages([]);

    _sessionId = await chatApi.createSession();

    _addMessage(
      message: Message(text: AppConfig.welcomeMessage, isUser: false),
    );

    await chatApi.warmup();
  }

  Future<Message?> sendMessage(String text) async {
    if (_sessionId == null) {
      throw Exception("Chat session not initialized.");
    }

    final trimmed = text.trim();
    if (trimmed.isEmpty) return null;

    _addMessage(message: Message(text: trimmed, isUser: true));

    _addMessage(message: Message(text: '', isUser: false, isLoading: true));

    try {
      final response = await chatApi.sendMessage(trimmed, _sessionId!);
      final botMessage = Message(text: response, isUser: false);

      _setMessages(chatService.removeLastBotMessage(messages.value));
      _addMessage(message: botMessage.copyWith(text: ''));

      await for (final partialText in chatService.streamText(response)) {
        _setMessages(
          chatService.replaceLastMessage(
            messages: messages.value,
            message: botMessage.copyWith(text: partialText),
          ),
        );
      }

      return botMessage;
    } catch (e) {
      _setMessages(chatService.removeLastBotMessage(messages.value));

      _addMessage(message: Message(text: 'Fehler: $e', isUser: false));

      return null;
    }
  }

  void _addMessage({required Message message}) {
    _setMessages(
      chatService.addMessage(messages: messages.value, message: message),
    );
  }

  void _setMessages(List<Message> updatedMessages) {
    messages.value = updatedMessages;
  }
}
