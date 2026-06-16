import 'dart:convert';

import 'package:app1/core/network/api_client.dart';
import 'package:app1/features/chatscreen/data/chat_api.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

void main() {
  // Test case references: documents/Testfaelle_Frontend_Aufgaben.md#t03-symptome-erkennen-input-drafts
  group('ChatApi input drafts', () {
    test('T03.2.1 loads draft symptoms from the session endpoint', () async {
      late Uri requestedUri;
      final api = ChatApi(
        ApiClient(
          MockClient((request) async {
            requestedUri = request.url;
            return http.Response(
              jsonEncode({
                'symptoms': ['Husten', 'Fieber'],
              }),
              200,
              headers: {'content-type': 'application/json'},
            );
          }),
        ),
      );

      final symptoms = await api.getInputDraftSymptoms('session-1');

      expect(requestedUri.path, '/input-drafts/session-1');
      expect(symptoms, ['Husten', 'Fieber']);
    });

    test('T03.2.2 updates draft symptoms with a PATCH request body', () async {
      late http.Request capturedRequest;
      final api = ChatApi(
        ApiClient(
          MockClient((request) async {
            capturedRequest = request;
            return http.Response(
              jsonEncode({
                'symptoms': ['Kopfschmerzen'],
              }),
              200,
              headers: {'content-type': 'application/json'},
            );
          }),
        ),
      );

      final symptoms = await api.updateInputDraftSymptoms('session-1', [
        'Kopfschmerzen',
      ]);

      expect(capturedRequest.method, 'PATCH');
      expect(capturedRequest.url.path, '/input-drafts/session-1');
      expect(jsonDecode(capturedRequest.body), {
        'symptoms': ['Kopfschmerzen'],
      });
      expect(symptoms, ['Kopfschmerzen']);
    });

    test('T03.2.3 cancels a draft through the session delete endpoint', () async {
      late http.Request capturedRequest;
      final api = ChatApi(
        ApiClient(
          MockClient((request) async {
            capturedRequest = request;
            return http.Response(
              jsonEncode({'message': 'deleted'}),
              200,
              headers: {'content-type': 'application/json'},
            );
          }),
        ),
      );

      await api.cancelInputDraft('session-1');

      expect(capturedRequest.method, 'DELETE');
      expect(capturedRequest.url.path, '/input-drafts/session-1');
    });
  });
}
