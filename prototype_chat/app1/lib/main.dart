import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

import 'core/network/api_client.dart';
import 'features/chat/data/chat_api.dart';
import 'features/chat/presentation/chat_controller.dart';
import 'features/chat/presentation/chat_screen.dart';

/// Einstiegspunkt der App.
///
/// Initialisiert Abhängigkeiten und startet die UI.
void main() {

  final client = ApiClient(http.Client());
  
  final api = ChatApi(client);
  final controller = ChatController(api);

  runApp(
    MaterialApp(
      home: ChatScreen(controller: controller),
    ),
  );
}