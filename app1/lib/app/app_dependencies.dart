import 'package:http/http.dart' as http;

import '../core/network/api_client.dart';
import '../features/chatscreen/controllers/chat_controller.dart';
import '../features/chatscreen/controllers/chat_warning_controller.dart';
import '../features/chatscreen/data/chat_api.dart';
import '../features/chatscreen/data/chat_history_repository.dart';
import '../features/chatscreen/services/chat_service.dart';
import '../features/chatscreen/services/chat_session_service.dart';
import '../features/chatscreen/services/symptom_draft_service.dart';
import '../features/authscreen/data/auth_api_service.dart';
import '../features/authscreen/state/auth_session.dart';
import '../features/symptom_diary/data/symptom_api_service.dart';
import '../features/symptom_diary/data/symptom_repository.dart';
import '../features/symptom_diary/data/symptom_sync_service.dart';
import '../features/profiles/data/profile_api_service.dart';

/// Composition root for services shared across multiple screens.
class AppDependencies {
  final http.Client _httpClient;
  final AuthSession authSession;
  late final ApiClient apiClient;
  late final ChatController chatController;
  late final ChatWarningController chatWarningController;
  late final AuthApiService authApiService;
  late final SymptomApiService symptomApiService;
  late final SymptomRepository symptomRepository;
  late final SymptomSyncService symptomSyncService;
  late final ProfileApiService profileApiService;

  AppDependencies({
    http.Client? httpClient,
    required this.authSession,
    SymptomRepository? symptomRepository,
  }) : _httpClient = httpClient ?? http.Client(),
       symptomRepository = symptomRepository ?? SymptomRepository() {
    apiClient = ApiClient(_httpClient);
    authSession.addListener(_syncAuthToken);
    _syncAuthToken();
    authApiService = AuthApiService(apiClient);
    symptomApiService = SymptomApiService(apiClient);
    symptomSyncService = SymptomSyncService(
      symptomApiService,
      repository: this.symptomRepository,
    );
    profileApiService = ProfileApiService(apiClient);
    final chatApi = ChatApi(apiClient);
    chatController = ChatController(
      chatApi: chatApi,
      chatService: ChatService(),
      chatSessionService: ChatSessionService(chatApi),
      symptomDraftService: SymptomDraftService(chatApi),
      chatHistoryRepository: ApiChatHistoryRepository(apiClient),
      authSession: authSession,
    );

    chatWarningController = ChatWarningController(profileApiService);
  }

  void _syncAuthToken() {
    final accessToken = authSession.accessToken;

    // Restored sessions bypass AuthApiService, so keep ApiClient in sync here.
    if (accessToken == null) {
      apiClient.clearAccessToken();
      return;
    }

    apiClient.setAccessToken(accessToken);
  }

  void dispose() {
    authSession.removeListener(_syncAuthToken);
    chatController.dispose();
    _httpClient.close();
  }
}
