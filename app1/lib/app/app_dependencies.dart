import 'package:http/http.dart' as http;

import '../core/network/api_client.dart';
import '../features/chatscreen/controllers/chat_controller.dart';
import '../features/chatscreen/data/chat_api.dart';
import '../features/chatscreen/services/chat_service.dart';
import '../features/chatscreen/services/chat_session_service.dart';
import '../features/chatscreen/services/symptom_draft_service.dart';
import '../features/authscreen/data/auth_api_service.dart';
import '../features/authscreen/state/auth_session.dart';

/// Composition root for services shared across multiple screens.
class AppDependencies {
  final http.Client _httpClient;
  late final ApiClient apiClient;
  late final ChatController chatController;
  late final AuthApiService authApiService;

  AppDependencies({http.Client? httpClient, required AuthSession authSession})
    : _httpClient = httpClient ?? http.Client() {
    apiClient = ApiClient(_httpClient);
    authApiService = AuthApiService(apiClient);
    final chatApi = ChatApi(apiClient);
    chatController = ChatController(
      chatApi: chatApi,
      chatService: ChatService(),
      chatSessionService: ChatSessionService(chatApi),
      symptomDraftService: SymptomDraftService(chatApi),
      authSession: authSession,
    );
  }

  void dispose() {
    chatController.dispose();
    _httpClient.close();
  }
}
