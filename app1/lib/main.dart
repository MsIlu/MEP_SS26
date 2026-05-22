import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'core/network/api_client.dart';
import 'features/chatscreen/controllers/chat_controller.dart';
import 'features/chatscreen/data/chat_api.dart';
import 'features/chatscreen/services/chat_service.dart';
import 'features/onboardingscreen/presentation/screens/onboarding_screen.dart';

void main() {
  runApp(const MyApp());
}

/// Root widget that wires together the app-wide dependencies and first screen.
class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    // Build the controller once at app startup so onboarding, home, and chat
    // share one chat session and one message history.
    final chatController = _buildChatController();

    return MaterialApp(
      debugShowCheckedModeBanner: false,

      title: 'Careena',

      theme: ThemeData(
        scaffoldBackgroundColor: Colors.white,
        useMaterial3: true,
      ),

      home: OnboardingScreen(chatController: chatController),
    );
  }

  /// Creates the chat dependency graph from the lowest HTTP layer upward.
  ChatController _buildChatController() {
    final httpClient = http.Client();
    final apiClient = ApiClient(httpClient);
    final chatApi = ChatApi(apiClient);

    return ChatController(chatApi: chatApi, chatService: ChatService());
  }
}