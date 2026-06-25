import 'dart:convert';

import 'package:app1/core/network/api_client.dart';
import 'package:app1/features/chatscreen/data/chat_history_repository.dart';
import 'package:app1/features/chatscreen/data/models/chat_history_entry.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

void main() {
  // Test case references: documents/Testfaelle_Frontend.md#t02-chat-history
  group('ApiChatHistoryRepository', () {
    test('T02.2.1 loads profile history sorted newest first', () async {
      late Uri requestedUri;
      final repository = ApiChatHistoryRepository(
        ApiClient(
          MockClient((request) async {
            requestedUri = request.url;
            return http.Response(
              jsonEncode([
                _historyJson(id: 1, createdAt: '2026-06-01T10:00:00+00:00'),
                _historyJson(id: 2, createdAt: '2026-06-03T10:00:00+00:00'),
              ]),
              200,
              headers: {'content-type': 'application/json'},
            );
          }),
        ),
      );

      final entries = await repository.loadEntries(profileId: 42);

      expect(requestedUri.path, '/chat-history/42');
      expect(entries.map((entry) => entry.id), ['2', '1']);
    });

    test('T02.2.2 saves completed chat history through the API', () async {
      late http.Request capturedRequest;
      final repository = ApiChatHistoryRepository(
        ApiClient(
          MockClient((request) async {
            capturedRequest = request;
            return http.Response(
              jsonEncode(
                _historyJson(id: 99, createdAt: '2026-06-03T12:00:00+00:00'),
              ),
              200,
              headers: {'content-type': 'application/json'},
            );
          }),
        ),
      );

      final savedEntry = await repository.saveCompletedChat(
        ChatHistoryEntry(
          id: 'local-1',
          profileId: 42,
          symptomTitle: 'Husten',
          isEmergency: false,
          createdAt: DateTime(2026, 6, 3, 12),
          messages: const [],
          recommendation: 'Hausarztpraxis regulaer',
          nextSteps: 'Termin vereinbaren',
        ),
      );

      final body = jsonDecode(capturedRequest.body) as Map<String, dynamic>;
      expect(capturedRequest.method, 'POST');
      expect(capturedRequest.url.path, '/chat-history');
      expect(body['profile_id'], 42);
      expect(body['title'], 'Husten');
      expect(body['status'], 'completed');
      expect(body['recommendation'], 'Hausarztpraxis regulaer');
      expect(body['next_steps'], 'Termin vereinbaren');
      expect(savedEntry.id, '99');
      expect(savedEntry.status, 'completed');
    });

    test('updates existing chat history through the API', () async {
      late http.Request capturedRequest;
      final repository = ApiChatHistoryRepository(
        ApiClient(
          MockClient((request) async {
            capturedRequest = request;
            return http.Response(
              jsonEncode(
                _historyJson(
                  id: 99,
                  createdAt: '2026-06-03T12:00:00+00:00',
                  status: 'active',
                ),
              ),
              200,
              headers: {'content-type': 'application/json'},
            );
          }),
        ),
      );

      final updatedEntry = await repository.updateChat(
        ChatHistoryEntry(
          id: '99',
          profileId: 42,
          symptomTitle: 'Husten',
          status: 'active',
          isEmergency: false,
          createdAt: DateTime(2026, 6, 3, 12),
          messages: const [],
          recommendation: '',
        ),
      );

      final body = jsonDecode(capturedRequest.body) as Map<String, dynamic>;
      expect(capturedRequest.method, 'PATCH');
      expect(capturedRequest.url.path, '/chat-history/99');
      expect(body['status'], 'active');
      expect(body['recommendation'], '');
      expect(updatedEntry.id, '99');
      expect(updatedEntry.status, 'active');
    });
  });
}

Map<String, dynamic> _historyJson({
  required int id,
  required String createdAt,
  String status = 'completed',
}) {
  return {
    'id': id,
    'profile_id': 42,
    'title': 'Husten',
    'status': status,
    'is_emergency': false,
    'created_at': createdAt,
    'updated_at': createdAt,
    'recommendation': 'Hausarztpraxis regulaer',
    'messages': const [],
  };
}
