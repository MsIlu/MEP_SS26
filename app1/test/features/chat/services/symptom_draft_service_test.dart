import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;

import 'package:app1/core/network/api_client.dart';
import 'package:app1/features/chatscreen/data/chat_api.dart';
import 'package:app1/features/chatscreen/services/symptom_draft_service.dart';

void main() {
  // Test case references: documents/Testfaelle_Frontend.md#t03-symptome-erkennen-input-drafts
  group('SymptomDraftService', () {
    test('returns empty symptoms without a session id', () async {
      final chatApi = _FakeChatApi();
      final service = SymptomDraftService(chatApi);

      expect(await service.loadSymptoms(null), isEmpty);
      expect(chatApi.loadedSessionIds, isEmpty);
    });

    test('loads and updates symptoms for a session', () async {
      final chatApi = _FakeChatApi();
      final service = SymptomDraftService(chatApi);

      final updated = await service.updateSymptoms('session-1', [
        'Husten',
        'Fieber',
      ]);
      final loaded = await service.loadSymptoms('session-1');

      expect(updated, ['Husten', 'Fieber']);
      expect(loaded, ['Husten', 'Fieber']);
    });

    test('clears draft data without throwing', () async {
      final chatApi = _FakeChatApi();
      final service = SymptomDraftService(chatApi);

      await service.updateSymptoms('session-1', ['Husten']);
      await service.cancelDraft('session-1');

      expect(await service.loadSymptoms('session-1'), isEmpty);
    });

    test('returns empty symptoms when loading fails', () async {
      final chatApi = _FakeChatApi()..shouldFailOnLoad = true;
      final service = SymptomDraftService(chatApi);

      expect(await service.loadSymptoms('session-1'), isEmpty);
      expect(chatApi.loadedSessionIds, ['session-1']);
    });

    test('requires an initialized session before updating symptoms', () async {
      final chatApi = _FakeChatApi();
      final service = SymptomDraftService(chatApi);

      await expectLater(
        service.updateSymptoms(null, ['Husten']),
        throwsA(isA<Exception>()),
      );
      expect(chatApi.symptomsBySession, isEmpty);
    });

    test('ignores cancel failures so the chat can continue', () async {
      final chatApi = _FakeChatApi()..shouldFailOnCancel = true;
      final service = SymptomDraftService(chatApi);

      await service.cancelDraft('session-1');

      expect(chatApi.cancelledSessionIds, ['session-1']);
    });
  });
}

class _FakeChatApi extends ChatApi {
  _FakeChatApi() : super(ApiClient(http.Client()));

  final Map<String, List<String>> symptomsBySession = {};
  final List<String> loadedSessionIds = [];
  final List<String> cancelledSessionIds = [];
  bool shouldFailOnLoad = false;
  bool shouldFailOnCancel = false;

  @override
  Future<List<String>> getInputDraftSymptoms(String sessionId) async {
    loadedSessionIds.add(sessionId);
    if (shouldFailOnLoad) {
      throw Exception('loading failed');
    }
    return symptomsBySession[sessionId] ?? [];
  }

  @override
  Future<List<String>> updateInputDraftSymptoms(
    String sessionId,
    List<String> symptoms,
  ) async {
    symptomsBySession[sessionId] = symptoms;
    return symptoms;
  }

  @override
  Future<void> cancelInputDraft(String sessionId) async {
    cancelledSessionIds.add(sessionId);
    if (shouldFailOnCancel) {
      throw Exception('cancel failed');
    }
    symptomsBySession.remove(sessionId);
  }
}
