import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

import 'package:app1/core/network/api_client.dart';
import 'package:app1/features/profiles/data/profile_api_service.dart';

void main() {
  group('ProfileApiService', () {
    test('getProfiles parses profile list and sends authorization header', () async {
      String? authorizationHeader;

      final mockHttpClient = MockClient((request) async {
        expect(request.method, 'GET');
        expect(request.url.path, contains('/profiles'));

        authorizationHeader = request.headers['Authorization'];

        return http.Response(
          jsonEncode([
            {
              'id': 10,
              'display_name': 'Anna',
              'date_of_birth': '2000-04-12',
              'biological_sex': 'female',
              'profile_type': 'self',
              'relevant_preconditions_summary': null,
              'relevant_medications_summary': null,
              'symptom_diary_summary': null,
              'role': 'owner',
            },
            {
              'id': 11,
              'display_name': 'Ben',
              'date_of_birth': '2015-08-20',
              'biological_sex': 'male',
              'profile_type': 'child',
              'relevant_preconditions_summary': 'Asthma',
              'relevant_medications_summary': 'Salbutamol bei Bedarf',
              'symptom_diary_summary': null,
              'role': 'guardian',
            },
          ]),
          200,
          headers: {'content-type': 'application/json'},
        );
      });

      final apiClient = ApiClient(mockHttpClient);
      apiClient.setAccessToken('test-token');

      final profileApiService = ProfileApiService(apiClient);

      final profiles = await profileApiService.getProfiles();

      expect(authorizationHeader, 'Bearer test-token');

      expect(profiles.length, 2);

      expect(profiles.first.id, 10);
      expect(profiles.first.displayName, 'Anna');
      expect(profiles.first.profileType, 'self');
      expect(profiles.first.role, 'owner');

      expect(profiles[1].id, 11);
      expect(profiles[1].displayName, 'Ben');
      expect(profiles[1].profileType, 'child');
      expect(profiles[1].relevantPreconditionsSummary, 'Asthma');
      expect(profiles[1].relevantMedicationsSummary, 'Salbutamol bei Bedarf');
      expect(profiles[1].role, 'guardian');
    });
  });
}