import 'dart:convert';

import 'package:app1/app/app_dependencies.dart';
import 'package:app1/features/authscreen/domain/models/account.dart';
import 'package:app1/features/authscreen/domain/models/auth_response.dart';
import 'package:app1/features/authscreen/state/auth_session.dart';
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
