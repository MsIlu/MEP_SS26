import 'dart:convert';

import 'package:app1/app/app_dependencies.dart';
import 'package:app1/features/authscreen/domain/models/account.dart';
import 'package:app1/features/authscreen/domain/models/auth_response.dart';
import 'package:app1/features/authscreen/state/auth_session.dart';
import 'package:app1/features/documents/data/document_repository.dart';
import 'package:app1/features/documents/data/models/document_entry.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('AppDependencies', () {
    setUp(() {
      SharedPreferences.setMockInitialValues({});
    });

    test('syncs restored auth token into ApiClient', () async {
      String? authorizationHeader;
      final session = AuthSession();
      final httpClient = MockClient((request) async {
        if (request.url.path.endsWith('/auth/me')) {
          authorizationHeader = request.headers['Authorization'];
          return http.Response(
            jsonEncode({'id': 1, 'email': 'test@example.com'}),
            200,
            headers: {'content-type': 'application/json'},
          );
        }

        return http.Response('Not found', 404);
      });
      final dependencies = AppDependencies(
        authSession: session,
        httpClient: httpClient,
      );

      addTearDown(dependencies.dispose);
      addTearDown(session.dispose);

      session.setAuthResponse(_authResponse());

      await dependencies.apiClient.get('/auth/me');

      expect(authorizationHeader, 'Bearer restored-token');
    });

    test('clears ApiClient token when auth session is cleared', () async {
      final seenAuthorizationHeaders = <String?>[];
      final session = AuthSession();
      final httpClient = MockClient((request) async {
        if (request.url.path.endsWith('/auth/me')) {
          seenAuthorizationHeaders.add(request.headers['Authorization']);
          return http.Response(
            jsonEncode({'id': 1, 'email': 'test@example.com'}),
            200,
            headers: {'content-type': 'application/json'},
          );
        }

        return http.Response('Not found', 404);
      });
      final dependencies = AppDependencies(
        authSession: session,
        httpClient: httpClient,
      );

      addTearDown(dependencies.dispose);
      addTearDown(session.dispose);

      session.setAuthResponse(_authResponse());
      await dependencies.apiClient.get('/auth/me');

      await session.clear();
      await dependencies.apiClient.get('/auth/me');

      expect(seenAuthorizationHeaders, ['Bearer restored-token', null]);
    });

    test('clears cached documents when auth session is cleared', () async {
      final session = AuthSession();
      final dependencies = AppDependencies(
        authSession: session,
        httpClient: MockClient((request) async => http.Response('{}', 200)),
      );
      final repository = DocumentRepository.instance;

      addTearDown(dependencies.dispose);
      addTearDown(session.dispose);
      addTearDown(repository.clear);

      session.setAuthResponse(_authResponse());
      repository.documents.value = [
        DocumentEntry(
          id: '1',
          profileId: 10,
          name: 'Befund.pdf',
          category: DocumentCategory.findings,
          createdAt: DateTime(2026, 6, 23),
          sizeInBytes: 3,
          source: DocumentSource.uploaded,
        ),
      ];
      repository.unreadCounts.value = {10: 1};

      await session.clear();

      expect(repository.documents.value, isEmpty);
      expect(repository.unreadCounts.value, isEmpty);
    });
  });
}

AuthResponse _authResponse() {
  return AuthResponse(
    accessToken: 'restored-token',
    tokenType: 'bearer',
    account: const Account(id: 1, email: 'test@example.com'),
    profiles: const [
      AuthProfile(
        id: 10,
        displayName: 'Anna',
        profileType: 'self',
        role: 'owner',
      ),
    ],
  );
}