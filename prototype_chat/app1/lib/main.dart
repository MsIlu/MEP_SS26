import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

import 'core/network/api_client.dart';
import 'features/chat/data/chat_api.dart';
import 'features/chat/presentation/chat_controller.dart';
import 'app/home_screen.dart';

/// Entry point of the application
///
/// Responsible for:
/// - Initializing dependencies
/// - Wiring API -> Controller -> UI
/// - Launching the Flutter app
/// 
/// Run with: (cd /app1)
/// flutter run
void main() {
  // --- Dependency setup ---
  final httpClient = http.Client();
  final apiClient = ApiClient(httpClient);
  final chatApi = ChatApi(apiClient);
  final chatController = ChatController(chatApi);

  // --- Start app ---
  runApp(
    MaterialApp(
      debugShowCheckedModeBanner: false,
      home: HomeScreen(controller: chatController),
    ),
  );
}