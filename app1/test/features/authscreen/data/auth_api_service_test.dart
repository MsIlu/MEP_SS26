import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

import 'package:app1/core/network/api_client.dart';
import 'package:app1/features/authscreen/data/auth_api_service.dart';

void main() {
  group('AuthApiService', () {
    test('login parses auth response and stores token in ApiClient', () async {
      String? authorizationHeaderForProtectedRequest;

      final mockHttpClient = MockClient((request) async {
        if (request.url.path.endsWith('/auth/login')) {
          expect(request.method, 'POST');

          final body = jsonDecode(request.body) as Map<String, dynamic>;
          expect(body['email'], 'test@example.com');
          expect(body['password'], '12345678');

          return http.Response(
            jsonEncode({
              'access_token': 'test-token',
              'token_type': 'bearer',
              'account': {
                'id': 1,
                'email': 'test@example.com',
              },
              'profiles': [
                {
                  'id': 10,
                  'display_name': 'Anna',
                  'profile_type': 'self',
                  'role': 'owner',
                }
              ],
            }),
            200,
            headers: {'content-type': 'application/json'},
          );
        }

        if (request.url.path.endsWith('/auth/me')) {
          expect(request.method, 'GET');

          authorizationHeaderForProtectedRequest =
          request.headers['Authorization'];

          return http.Response(
            jsonEncode({
              'id': 1,
              'email': 'test@example.com',
            }),
            200,
            headers: {'content-type': 'application/json'},
          );
        }

        return http.Response('Not found', 404);
      });

      final apiClient = ApiClient(mockHttpClient);
      final authApiService = AuthApiService(apiClient);

      final response = await authApiService.login(
        email: 'test@example.com',
        password: '12345678',
      );

      expect(response.accessToken, 'test-token');
      expect(response.account.email, 'test@example.com');
      expect(response.profiles.length, 1);
      expect(response.profiles.first.id, 10);
      expect(response.profiles.first.role, 'owner');

      await apiClient.get('/auth/me');

      expect(
        authorizationHeaderForProtectedRequest,
        'Bearer test-token',
      );
    });
  });
}