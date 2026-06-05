import 'package:http/http.dart' as http;

import '../core/network/api_client.dart';
import '../features/chatscreen/controllers/chat_controller.dart';
import '../features/chatscreen/controllers/chat_warning_controller.dart';
import '../features/chatscreen/data/chat_api.dart';
import '../features/chatscreen/services/chat_service.dart';

/// Composition root for services shared across multiple screens.
class AppDependencies {
  final http.Client _httpClient;
  late final ApiClient apiClient;
  late final ChatController chatController;
  late final ChatWarningController chatWarningController;

  AppDependencies({http.Client? httpClient})
    : _httpClient = httpClient ?? http.Client() {
    apiClient = ApiClient(_httpClient);
    chatController = ChatController(
      chatApi: ChatApi(apiClient),
      chatService: ChatService(),
    );

    chatWarningController = ChatWarningController();
  }

  void dispose() {
    chatController.dispose();
    _httpClient.close();
  }
}