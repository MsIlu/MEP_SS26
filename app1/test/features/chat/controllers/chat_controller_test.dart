import 'dart:async';

import 'package:flutter_test/flutter_test.dart';
import 'package:app1/core/network/api_client.dart';
import 'package:app1/core/network/api_exception.dart';
import 'package:app1/features/authscreen/domain/models/account.dart';
import 'package:app1/features/authscreen/domain/models/auth_response.dart';
import 'package:app1/features/authscreen/state/auth_session.dart';
import 'package:app1/features/chatscreen/controllers/chat_controller.dart';
import 'package:app1/features/chatscreen/data/chat_api.dart';
import 'package:app1/features/chatscreen/data/chat_history_repository.dart';
import 'package:app1/features/chatscreen/data/models/careena_availability.dart';
import 'package:app1/features/chatscreen/data/models/chat_history_entry.dart';
import 'package:app1/features/chatscreen/data/models/chat_response_model.dart';
import 'package:app1/features/chatscreen/services/chat_service.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

/// Unit tests for chat controller state and profile-aware chat requests.
void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  SharedPreferences.setMockInitialValues({});

  // Test case references: documents/Testfaelle_Frontend.md#t02-chat-history
  group('ChatController', () {
    test('starts with an empty message list before initialization', () {
      final httpClient = http.Client();
      final apiClient = ApiClient(httpClient);
      final authSession = AuthSession();

      final controller = ChatController(
        chatApi: ChatApi(apiClient),
        chatService: ChatService(),
        authSession: authSession,
        chatHistoryRepository: _FakeChatHistoryRepository(),
      );

      addTearDown(controller.dispose);
      addTearDown(authSession.dispose);
      addTearDown(httpClient.close);

      expect(controller.messages.value, isEmpty);
    });

    test('warms up LLM status before the first availability check', () async {
      final authSession = AuthSession();
      final chatApi = _FakeChatApi();
      final controller = ChatController(
        chatApi: chatApi,
        chatService: ChatService(),
        authSession: authSession,
        chatHistoryRepository: _FakeChatHistoryRepository(),
      );

      addTearDown(controller.dispose);
      addTearDown(authSession.dispose);

      await controller.init();

      expect(chatApi.operationLog, [
        'createSession',
        'warmup',
        'getCareenaAvailability',
        'getInputDraftSymptoms',
      ]);
    });

    test('refreshes LLM status when an initialized chat is opened again', () async {
      final authSession = AuthSession();
      final chatApi = _FakeChatApi();
      final controller = ChatController(
        chatApi: chatApi,
        chatService: ChatService(),
        authSession: authSession,
        chatHistoryRepository: _FakeChatHistoryRepository(),
      );

      addTearDown(controller.dispose);
      addTearDown(authSession.dispose);

      await controller.init();
      chatApi.operationLog.clear();

      await controller.init();

      expect(chatApi.operationLog, [
        'warmup',
        'getCareenaAvailability',
      ]);
    });

    test('sends active profile id from auth session to chat api', () async {
      final authSession = AuthSession();
      final chatApi = _FakeChatApi();
      final controller = ChatController(
        chatApi: chatApi,
        chatService: ChatService(),
        authSession: authSession,
        chatHistoryRepository: _FakeChatHistoryRepository(),
      );

      addTearDown(controller.dispose);
      addTearDown(authSession.dispose);

      authSession.setAuthResponse(
        AuthResponse(
          accessToken: 'test-token',
          tokenType: 'bearer',
          account: const Account(id: 1, email: 'test@example.com'),
          profiles: const [
            AuthProfile(
              id: 42,
              displayName: 'Anna',
              profileType: 'self',
              role: 'owner',
            ),
          ],
        ),
      );

      await controller.init();
      final response = await controller.sendMessage('Hallo');

      expect(response, isNotNull);
      expect(chatApi.lastText, 'Hallo');
      expect(chatApi.lastSessionId, 'fake-session-1');
      expect(chatApi.lastProfileId, 42);
    });

    test('requests recommendation through dedicated backend endpoint', () async {
      final authSession = AuthSession();
      final chatApi = _FakeChatApi();
      final controller = ChatController(
        chatApi: chatApi,
        chatService: ChatService(),
        authSession: authSession,
        chatHistoryRepository: _FakeChatHistoryRepository(),
      );

      addTearDown(controller.dispose);
      addTearDown(authSession.dispose);

      await controller.init();
      await controller.requestRecommendation();

      expect(chatApi.requestRecommendationSessionIds, ['fake-session-1']);
      expect(chatApi.sentTexts, isEmpty);
      expect(
        controller.messages.value.where((message) => message.isUser).last.text,
        ChatController.recommendationRequestDisplayText,
      );
    });

    test('resets chat session and draft when active profile changes', () async {
      final authSession = AuthSession();
      final chatApi = _FakeChatApi();
      final controller = ChatController(
        chatApi: chatApi,
        chatService: ChatService(),
        authSession: authSession,
        chatHistoryRepository: _FakeChatHistoryRepository(),
      );

      addTearDown(controller.dispose);
      addTearDown(authSession.dispose);

      authSession.setAuthResponse(
        AuthResponse(
          accessToken: 'test-token',
          tokenType: 'bearer',
          account: const Account(id: 1, email: 'test@example.com'),
          profiles: const [
            AuthProfile(
              id: 42,
              displayName: 'Anna',
              profileType: 'self',
              role: 'owner',
            ),
            AuthProfile(
              id: 43,
              displayName: 'Ben',
              profileType: 'child',
              role: 'guardian',
            ),
          ],
        ),
      );

      await controller.init();
      await controller.updateSymptomsDirectly(['Kopfschmerzen']);

      authSession.setActiveProfileById(43);
      await Future<void>.delayed(Duration.zero);
      await Future<void>.delayed(Duration.zero);

      expect(chatApi.cancelledSessionIds, contains('fake-session-1'));
      expect(controller.symptoms.value, isEmpty);
      expect(controller.chatSessionService.profileId, 43);
      expect(chatApi.createdProfileIds, [42, 43]);
    });

    test(
      'does not show a delayed response after the profile changes',
      () async {
        final authSession = AuthSession();
        final chatApi = _FakeChatApi();
        final delayedResponse = Completer<ChatResponse>();
        chatApi.responseCompleter = delayedResponse;
        final historyRepository = _FakeChatHistoryRepository();
        final controller = ChatController(
          chatApi: chatApi,
          chatService: ChatService(),
          authSession: authSession,
          chatHistoryRepository: historyRepository,
        );

        addTearDown(controller.dispose);
        addTearDown(authSession.dispose);

        authSession.setAuthResponse(
          AuthResponse(
            accessToken: 'test-token',
            tokenType: 'bearer',
            account: const Account(id: 1, email: 'test@example.com'),
            profiles: const [
              AuthProfile(
                id: 42,
                displayName: 'Anna',
                profileType: 'self',
                role: 'owner',
              ),
              AuthProfile(
                id: 43,
                displayName: 'Ben',
                profileType: 'child',
                role: 'guardian',
              ),
            ],
          ),
        );

        await controller.init();
        final pendingResponse = controller.sendMessage('Nachricht fuer Anna');
        while (chatApi.sentTexts.isEmpty) {
          await Future<void>.delayed(Duration.zero);
        }

        authSession.setActiveProfileById(43);
        delayedResponse.complete(
          const ChatResponse(text: 'Antwort fuer Anna', redFlag: false),
        );
        await pendingResponse;
        await Future<void>.delayed(Duration.zero);

        expect(authSession.activeProfileId, 43);
        expect(controller.chatSessionService.profileId, 43);
        expect(
          controller.messages.value.map((message) => message.text),
          isNot(contains('Antwort fuer Anna')),
        );
        expect(historyRepository.savedEntries.single.profileId, 42);
      },
    );

    test(
      'saves recommendation history and blocks follow-up messages',
      () async {
        final authSession = AuthSession();
        authSession.setAuthResponse(
          AuthResponse(
            accessToken: 'test-token',
            tokenType: 'bearer',
            account: const Account(id: 1, email: 'test@example.com'),
            profiles: const [
              AuthProfile(
                id: 42,
                displayName: 'Anna',
                profileType: 'self',
                role: 'owner',
              ),
            ],
          ),
        );
        final chatApi = _FakeChatApi()
          ..nextResponse = const ChatResponse(
            text: 'Bitte heute aerztlich abklaeren.',
            redFlag: false,
            responseMode: 'recommend',
            recommendationReady: true,
            recommendationResult: RecommendationResult(
              allowed: true,
              summary: 'Bitte heute aerztlich abklaeren.',
              urgency: 'soon',
              urgencyLevel: 'moderate',
              careLevel: 'general_practice',
              specialty: 'general_practice',
              nextStep: 'Termin vereinbaren',
            ),
          );
        final historyRepository = _FakeChatHistoryRepository();
        final controller = ChatController(
          chatApi: chatApi,
          chatService: ChatService(),
          authSession: authSession,
          chatHistoryRepository: historyRepository,
        );

        addTearDown(controller.dispose);
        addTearDown(authSession.dispose);

        await controller.init();
        await controller.updateSymptomsDirectly(['Kopfschmerzen']);
        final response = await controller.sendMessage('Ich habe Schmerzen');
        final secondResponse = await controller.sendMessage('Noch eine Frage');

        expect(response, isNotNull);
        expect(secondResponse, isNull);
        expect(controller.isCompleted.value, isTrue);
        expect(chatApi.sentTexts, ['Ich habe Schmerzen']);
        expect(historyRepository.savedEntries, hasLength(1));
        expect(
          historyRepository.savedEntries.single.status,
          'waiting_for_assistant',
        );
        expect(historyRepository.updatedEntries.last.status, 'completed');
        expect(historyRepository.updatedEntries.last.profileId, 42);
        expect(
          historyRepository.updatedEntries.last.symptomTitle,
          'Kopfschmerzen',
        );
        expect(historyRepository.updatedEntries.last.isEmergency, isFalse);
        expect(
          historyRepository.updatedEntries.last.recommendation,
          'Bitte heute aerztlich abklaeren.',
        );
      },
    );

    test('completes anonymous recommendation without saving history', () async {
      final authSession = AuthSession();
      final chatApi = _FakeChatApi()
        ..nextResponse = const ChatResponse(
          text: 'Bitte heute aerztlich abklaeren.',
          redFlag: false,
          responseMode: 'recommend',
          recommendationReady: true,
          recommendationResult: RecommendationResult(
            allowed: true,
            summary: 'Bitte heute aerztlich abklaeren.',
            urgency: 'soon',
            urgencyLevel: 'moderate',
            careLevel: 'general_practice',
            specialty: 'general_practice',
            nextStep: 'Termin vereinbaren',
          ),
        );
      final historyRepository = _FakeChatHistoryRepository();
      final controller = ChatController(
        chatApi: chatApi,
        chatService: ChatService(),
        authSession: authSession,
        chatHistoryRepository: historyRepository,
      );

      addTearDown(controller.dispose);
      addTearDown(authSession.dispose);

      await controller.init();
      final response = await controller.sendMessage('Ich habe Schmerzen');

      expect(response, isNotNull);
      expect(controller.isCompleted.value, isTrue);
      expect(historyRepository.savedEntries, isEmpty);
    });

    test('saves red flag recommendation history and completes chat', () async {
      final authSession = AuthSession();
      authSession.setAuthResponse(
        AuthResponse(
          accessToken: 'test-token',
          tokenType: 'bearer',
          account: const Account(id: 1, email: 'test@example.com'),
          profiles: const [
            AuthProfile(
              id: 42,
              displayName: 'Anna',
              profileType: 'self',
              role: 'owner',
            ),
          ],
        ),
      );
      final chatApi = _FakeChatApi()
        ..nextResponse = const ChatResponse(
          text: 'Bitte sofort den Notruf 112 kontaktieren.',
          redFlag: true,
          action: 'Notruf 112',
          ruleName: 'Starke Blutung',
        );
      final historyRepository = _FakeChatHistoryRepository();
      final controller = ChatController(
        chatApi: chatApi,
        chatService: ChatService(),
        authSession: authSession,
        chatHistoryRepository: historyRepository,
      );

      addTearDown(controller.dispose);
      addTearDown(authSession.dispose);

      await controller.init();
      await controller.updateSymptomsDirectly(['Blutung']);
      final response = await controller.sendMessage('Ich blute stark');
      final secondResponse = await controller.sendMessage('Noch eine Frage');

      expect(response?.redFlag, isTrue);
      expect(secondResponse, isNull);
      expect(controller.isCompleted.value, isTrue);
      expect(historyRepository.savedEntries, hasLength(1));
      expect(
        historyRepository.savedEntries.single.status,
        'waiting_for_assistant',
      );
      expect(historyRepository.updatedEntries.last.status, 'completed');
      expect(historyRepository.updatedEntries.last.symptomTitle, 'Blutung');
      expect(historyRepository.updatedEntries.last.isEmergency, isTrue);
      expect(
        historyRepository.updatedEntries.last.recommendation,
        'Bitte sofort den Notruf 112 kontaktieren.',
      );
    });

    test('treats notruf recommendation text as emergency history', () async {
      final authSession = AuthSession();
      authSession.setAuthResponse(
        AuthResponse(
          accessToken: 'test-token',
          tokenType: 'bearer',
          account: const Account(id: 1, email: 'test@example.com'),
          profiles: const [
            AuthProfile(
              id: 42,
              displayName: 'Anna',
              profileType: 'self',
              role: 'owner',
            ),
          ],
        ),
      );
      final chatApi = _FakeChatApi()
        ..nextResponse = const ChatResponse(
          text:
              'Wichtiger Hinweis:\nDeine Angaben koennen auf eine akute Notfallsituation hinweisen.\n\nNächster Schritt:\nBitte wähle sofort den Notruf 112.',
          redFlag: false,
          action: 'Notruf 112',
        );
      final historyRepository = _FakeChatHistoryRepository();
      final controller = ChatController(
        chatApi: chatApi,
        chatService: ChatService(),
        authSession: authSession,
        chatHistoryRepository: historyRepository,
      );

      addTearDown(controller.dispose);
      addTearDown(authSession.dispose);

      await controller.init();
      await controller.updateSymptomsDirectly(['Atemnot']);
      final response = await controller.sendMessage('Ich habe Atemnot');

      expect(response?.redFlag, isFalse);
      expect(controller.isCompleted.value, isTrue);
      expect(historyRepository.savedEntries, hasLength(1));
      expect(
        historyRepository.savedEntries.single.status,
        'waiting_for_assistant',
      );
      expect(historyRepository.updatedEntries.last.status, 'completed');
      expect(historyRepository.updatedEntries.last.symptomTitle, 'Atemnot');
      expect(historyRepository.updatedEntries.last.isEmergency, isTrue);
    });

    test('treats urgent red flag metadata as emergency history', () async {
      final authSession = AuthSession();
      authSession.setAuthResponse(
        AuthResponse(
          accessToken: 'test-token',
          tokenType: 'bearer',
          account: const Account(id: 1, email: 'test@example.com'),
          profiles: const [
            AuthProfile(
              id: 42,
              displayName: 'Anna',
              profileType: 'self',
              role: 'owner',
            ),
          ],
        ),
      );
      final chatApi = _FakeChatApi()
        ..nextResponse = const ChatResponse(
          text: 'Bitte hole umgehend medizinische Hilfe.',
          redFlag: false,
          severity: 'sofort',
          category: 'emergency',
          matchedKeywords: ['starke atemnot'],
        );
      final historyRepository = _FakeChatHistoryRepository();
      final controller = ChatController(
        chatApi: chatApi,
        chatService: ChatService(),
        authSession: authSession,
        chatHistoryRepository: historyRepository,
      );

      addTearDown(controller.dispose);
      addTearDown(authSession.dispose);

      await controller.init();
      await controller.updateSymptomsDirectly(['Atemnot']);
      await controller.sendMessage('Ich bekomme schlecht Luft');

      expect(controller.isCompleted.value, isTrue);
      expect(
        historyRepository.savedEntries.single.status,
        'waiting_for_assistant',
      );
      expect(historyRepository.updatedEntries.last.status, 'completed');
      expect(historyRepository.updatedEntries.last.isEmergency, isTrue);
    });

    test('rechecks limited availability before sending a message', () async {
      final authSession = AuthSession();
      final chatApi = _FakeChatApi()
        ..nextAvailability = CareenaAvailability.limited;
      final controller = ChatController(
        chatApi: chatApi,
        chatService: ChatService(),
        authSession: authSession,
        chatHistoryRepository: _FakeChatHistoryRepository(),
      );

      addTearDown(controller.dispose);
      addTearDown(authSession.dispose);

      await controller.init();
      expect(controller.availability.value, CareenaAvailability.limited);

      chatApi.nextAvailability = CareenaAvailability.online;
      final response = await controller.sendMessage('Hallo');

      expect(response, isNotNull);
      expect(chatApi.availabilityRequests, 2);
      expect(controller.availability.value, CareenaAvailability.online);
      expect(chatApi.sentTexts, ['Hallo']);
    });

    test('updates availability after a send error', () async {
      final authSession = AuthSession();
      final chatApi = _FakeChatApi()..throwOnSend = true;
      final controller = ChatController(
        chatApi: chatApi,
        chatService: ChatService(),
        authSession: authSession,
        chatHistoryRepository: _FakeChatHistoryRepository(),
      );

      addTearDown(controller.dispose);
      addTearDown(authSession.dispose);

      await controller.init();

      chatApi.nextAvailability = CareenaAvailability.offline;
      final response = await controller.sendMessage('Hallo');

      expect(response, isNull);
      expect(controller.availability.value, CareenaAvailability.offline);
    });

    test('shows a friendly chat message for network errors', () async {
      final authSession = AuthSession();
      final chatApi = _FakeChatApi()
        ..sendError = const ApiException(ApiErrorType.network, 'Network Error');
      final controller = ChatController(
        chatApi: chatApi,
        chatService: ChatService(),
        authSession: authSession,
        chatHistoryRepository: _FakeChatHistoryRepository(),
      );

      addTearDown(controller.dispose);
      addTearDown(authSession.dispose);

      await controller.init();
      final response = await controller.sendMessage('Hallo');

      expect(response, isNull);
      expect(
        controller.messages.value.last.text,
        contains('Careena kann den Server gerade nicht erreichen.'),
      );
      expect(controller.messages.value.last.text, isNot(contains('Exception')));
    });
  });
}

class _FakeChatApi extends ChatApi {
  _FakeChatApi() : super(ApiClient(http.Client()));

  String? lastText;
  String? lastSessionId;
  int? lastProfileId;
  ChatResponse nextResponse = const ChatResponse(
    text: 'Antwort',
    redFlag: false,
    action: null,
  );
  int createSessionCalls = 0;
  final List<int?> createdProfileIds = [];
  final List<String> cancelledSessionIds = [];
  final List<String> sentTexts = [];
  final List<String> operationLog = [];
  final List<String> requestRecommendationSessionIds = [];
  List<String> symptoms = [];
  Completer<ChatResponse>? responseCompleter;
  CareenaAvailability nextAvailability = CareenaAvailability.online;
  int availabilityRequests = 0;
  bool throwOnSend = false;
  ApiException? sendError;

  @override
  Future<String> createSession([int? profileId]) async {
    createSessionCalls += 1;
    createdProfileIds.add(profileId);
    operationLog.add('createSession');
    return 'fake-session-$createSessionCalls';
  }

  @override
  Future<void> warmup() async {
    operationLog.add('warmup');
  }

  @override
  Future<CareenaAvailability> getCareenaAvailability() async {
    availabilityRequests += 1;
    operationLog.add('getCareenaAvailability');
    return nextAvailability;
  }

  @override
  Future<ChatResponse> sendMessage(
    String text,
    String sessionId,
    int? profileId,
  ) async {
    if (throwOnSend) {
      throw Exception('send failed');
    }

    final error = sendError;
    if (error != null) {
      throw error;
    }

    lastText = text;
    lastSessionId = sessionId;
    lastProfileId = profileId;
    sentTexts.add(text);

    return responseCompleter?.future ?? nextResponse;
  }

  @override
  Future<ChatResponse> requestRecommendation(String sessionId) async {
    requestRecommendationSessionIds.add(sessionId);
    return nextResponse;
  }

  @override
  Future<List<String>> getInputDraftSymptoms(String sessionId) async {
    operationLog.add('getInputDraftSymptoms');
    return symptoms;
  }

  @override
  Future<List<String>> updateInputDraftSymptoms(
    String sessionId,
    List<String> symptoms,
  ) async {
    this.symptoms = symptoms;
    return symptoms;
  }

  @override
  Future<void> cancelInputDraft(String sessionId) async {
    cancelledSessionIds.add(sessionId);
    symptoms = [];
  }
}

class _FakeChatHistoryRepository extends ChatHistoryRepository {
  final List<ChatHistoryEntry> savedEntries = [];
  final List<ChatHistoryEntry> updatedEntries = [];

  @override
  Future<List<ChatHistoryEntry>> loadEntries({required int profileId}) async {
    return savedEntries.where((entry) => entry.profileId == profileId).toList();
  }

  @override
  Future<ChatHistoryEntry> saveChat(ChatHistoryEntry entry) async {
    final savedEntry = ChatHistoryEntry(
      id: 'history-${savedEntries.length + 1}',
      profileId: entry.profileId,
      sessionId: entry.sessionId,
      symptomTitle: entry.symptomTitle,
      status: entry.status,
      isEmergency: entry.isEmergency,
      createdAt: entry.createdAt,
      updatedAt: entry.updatedAt,
      messages: entry.messages,
      recommendation: entry.recommendation,
      nextSteps: entry.nextSteps,
    );

    savedEntries.add(savedEntry);
    return savedEntry;
  }

  @override
  Future<ChatHistoryEntry> updateChat(ChatHistoryEntry entry) async {
    updatedEntries.add(entry);
    return entry;
  }

  @override
  Future<ChatHistoryEntry> saveCompletedChat(ChatHistoryEntry entry) async {
    return saveChat(entry);
  }
}
