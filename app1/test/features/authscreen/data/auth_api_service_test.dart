import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

import 'package:app1/core/network/api_client.dart';
import 'package:app1/features/authscreen/data/auth_api_service.dart';

void main() {
  // Test case references: documents/Testfaelle_Frontend.md#t04-auth-und-registrierung
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
              'account': {'id': 1, 'email': 'test@example.com'},
              'profiles': [
                {
                  'id': 10,
                  'display_name': 'Anna',
                  'profile_type': 'self',
                  'role': 'owner',
                },
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
            jsonEncode({'id': 1, 'email': 'test@example.com'}),
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

      expect(authorizationHeaderForProtectedRequest, 'Bearer test-token');
    });

    test(
      'register parses auth response and stores token in ApiClient',
      () async {
        String? authorizationHeaderForProtectedRequest;

        final mockHttpClient = MockClient((request) async {
          if (request.url.path.endsWith('/auth/register')) {
            expect(request.method, 'POST');

            final body = jsonDecode(request.body) as Map<String, dynamic>;
            expect(body['email'], 'new@example.com');
            expect(body['password'], '12345678');
            expect(body['display_name'], 'Anna');
            expect(body['date_of_birth'], '2000-04-12');
            expect(body['biological_sex'], 'female');
            expect(body['height_cm'], 170);
            expect(body['weight_kg'], 70.5);
            expect(body['relevant_preconditions_summary'], 'Asthma');
            expect(body['symptom_diary_summary'], 'Keine akuten Beschwerden');

            return http.Response(
              jsonEncode({
                'access_token': 'register-token',
                'token_type': 'bearer',
                'account': {'id': 2, 'email': 'new@example.com'},
                'profiles': [
                  {
                    'id': 20,
                    'display_name': 'Anna',
                    'profile_type': 'self',
                    'role': 'owner',
                  },
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
              jsonEncode({'id': 2, 'email': 'new@example.com'}),
              200,
              headers: {'content-type': 'application/json'},
            );
          }

          return http.Response('Not found', 404);
        });

        final apiClient = ApiClient(mockHttpClient);
        final authApiService = AuthApiService(apiClient);

        final response = await authApiService.register(
          email: 'new@example.com',
          password: '12345678',
          displayName: 'Anna',
          dateOfBirth: '2000-04-12',
          biologicalSex: 'female',
          heightCm: 170,
          weightKg: 70.5,
          relevantPreconditionsSummary: 'Asthma',
          symptomDiarySummary: 'Keine akuten Beschwerden',
        );

        expect(response.accessToken, 'register-token');
        expect(response.account.id, 2);
        expect(response.account.email, 'new@example.com');
        expect(response.profiles.length, 1);
        expect(response.profiles.first.id, 20);
        expect(response.profiles.first.displayName, 'Anna');
        expect(response.profiles.first.profileType, 'self');
        expect(response.profiles.first.role, 'owner');

        await apiClient.get('/auth/me');

        expect(authorizationHeaderForProtectedRequest, 'Bearer register-token');
      },
    );

    test(
      'register parses auth response and stores token in ApiClient',
      () async {
        String? authorizationHeaderForProtectedRequest;

        final mockHttpClient = MockClient((request) async {
          if (request.url.path.endsWith('/auth/register')) {
            expect(request.method, 'POST');

            final body = jsonDecode(request.body) as Map<String, dynamic>;
            expect(body['email'], 'new@example.com');
            expect(body['password'], '12345678');
            expect(body['display_name'], 'Anna');
            expect(body['date_of_birth'], '2000-04-12');
            expect(body['biological_sex'], 'female');

            return http.Response(
              jsonEncode({
                'access_token': 'register-token',
                'token_type': 'bearer',
                'account': {'id': 2, 'email': 'new@example.com'},
                'profiles': [
                  {
                    'id': 20,
                    'display_name': 'Anna',
                    'profile_type': 'self',
                    'role': 'owner',
                  },
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
              jsonEncode({'id': 2, 'email': 'new@example.com'}),
              200,
              headers: {'content-type': 'application/json'},
            );
          }

          return http.Response('Not found', 404);
        });

        final apiClient = ApiClient(mockHttpClient);
        final authApiService = AuthApiService(apiClient);

        final response = await authApiService.register(
          email: 'new@example.com',
          password: '12345678',
          displayName: 'Anna',
          dateOfBirth: '2000-04-12',
          biologicalSex: 'female',
        );

        expect(response.accessToken, 'register-token');
        expect(response.account.id, 2);
        expect(response.account.email, 'new@example.com');
        expect(response.profiles.length, 1);
        expect(response.profiles.first.id, 20);
        expect(response.profiles.first.displayName, 'Anna');
        expect(response.profiles.first.profileType, 'self');
        expect(response.profiles.first.role, 'owner');

        await apiClient.get('/auth/me');

        expect(authorizationHeaderForProtectedRequest, 'Bearer register-token');
      },
    );
  });
}
