import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'core/network/api_client.dart';
import 'features/chat/data/chat_api.dart';
import 'features/chat/controllers/chat_controller.dart';
import 'features/chat/presentation/screens/home_screen.dart';

/// Entry point of the application.
///
/// This file is responsible for:
/// - Initializing core dependencies
/// - Wiring API layer → Controller → UI
/// - Launching the Flutter application
///
/// Run the app with:
/// `flutter run` (from the /app1 directory)
void main() {
  /// -----------------------------
  /// Dependency Initialization
  /// -----------------------------

  final httpClient = http.Client();
  final apiClient = ApiClient(httpClient);
  final chatApi = ChatApi(apiClient);
  final chatController = ChatController(chatApi);

  /// -----------------------------
  /// App Startup
  /// -----------------------------

  runApp(
    MaterialApp(
      debugShowCheckedModeBanner: false,
      home: HomeScreen(controller: chatController),
    ),
  );
}