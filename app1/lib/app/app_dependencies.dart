import 'package:http/http.dart' as http;

import '../core/network/api_client.dart';
import '../features/chatscreen/controllers/chat_controller.dart';
import '../features/chatscreen/controllers/chat_warning_controller.dart';
import '../features/chatscreen/data/chat_api.dart';
import '../features/chatscreen/services/chat_service.dart';
import '../features/authscreen/data/auth_api_service.dart';
import '../features/authscreen/state/auth_session.dart';
import '../features/profiles/data/profile_api_service.dart';

/// Composition root for services shared across multiple screens.
class AppDependencies {
  final http.Client _httpClient;
  late final ApiClient apiClient;
  late final ChatController chatController;
  late final ChatWarningController chatWarningController;
  late final AuthApiService authApiService;
  late final ProfileApiService profileApiService;

  AppDependencies({
    http.Client? httpClient,
    required AuthSession authSession,
  })
    : _httpClient = httpClient ?? http.Client() {
    apiClient = ApiClient(_httpClient);
    authApiService = AuthApiService(apiClient);
    profileApiService = ProfileApiService(apiClient);
    chatController = ChatController(
      chatApi: ChatApi(apiClient),
      chatService: ChatService(),
      authSession: authSession,
    );

    chatWarningController = ChatWarningController(profileApiService);
  }

  void dispose() {
    chatController.dispose();
    _httpClient.close();
  }
}
