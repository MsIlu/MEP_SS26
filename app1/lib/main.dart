import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'core/network/api_client.dart';
import 'features/chat/controllers/chat_controller.dart';
import 'features/chat/data/chat_api.dart';
import 'features/chat/services/chat_service.dart';
import 'features/onboardingscreen/presentation/screens/onboarding_screen.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
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

  ChatController _buildChatController() {
    final httpClient = http.Client();
    final apiClient = ApiClient(httpClient);
    final chatApi = ChatApi(apiClient);

    return ChatController(chatApi: chatApi, chatService: ChatService());
  }
}
