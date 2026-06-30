import 'dart:convert';

import 'package:app1/core/network/api_client.dart';
import 'package:app1/features/symptom_diary/data/symptom_api_service.dart';
import 'package:app1/features/symptom_diary/data/symptom_entry.dart';
import 'package:app1/features/symptom_diary/data/symptom_repository.dart';
import 'package:app1/features/symptom_diary/data/symptom_sync_service.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  // Test case references: documents/Testfaelle_Frontend.md#t09-symptom-diary
  group('SymptomSyncService', () {
    setUp(() {
      SharedPreferences.setMockInitialValues({});
    });

    test(
      'replaces stale cache with database entries for the selected profile',
      () async {
        final repository = SymptomRepository();
        await repository.saveEntries([
          SymptomEntry(
            id: 10,
            date: DateTime(2026, 6, 17),
            symptom: 'Alter Profil-Cache',
            intensity: 5,
            note: 'Darf nach Profilwechsel nicht bleiben',
            createdAt: DateTime(2026, 6, 17, 8),
          ),
        ]);

        final requestedPaths = <String>[];
        final apiClient = ApiClient(
          MockClient((request) async {
            requestedPaths.add(request.url.path);

            return http.Response(
              jsonEncode([
                {
                  'id': 42,
                  'profile_id': 11,
                  'date': '2026-06-18T00:00:00.000',
                  'symptom': 'Neues Profil aus DB',
                  'bodyArea': 'Kopf',
                  'intensity': 7,
                  'note': 'Aus der API geladen',
                  'createdAt': '2026-06-18T09:00:00.000',
                },
              ]),
              200,
              headers: {'content-type': 'application/json'},
            );
          }),
        );

        final service = SymptomSyncService(
          SymptomApiService(apiClient),
          repository: repository,
        );

        await service.syncActiveProfile(11);

        final entries = await repository.loadEntries();
        expect(requestedPaths, ['/profiles/11/symptoms']);
        expect(entries, hasLength(1));
        expect(entries.single.id, 42);
        expect(entries.single.symptom, 'Neues Profil aus DB');
        expect(entries.single.isSynced, isTrue);
        expect(
          entries.map((entry) => entry.symptom),
          isNot(contains('Alter Profil-Cache')),
        );
      },
    );
  });

  group('SymptomApiService', () {
    test('updates a symptom entry through the profile endpoint', () async {
      final requestedPaths = <String>[];
      final requestBodies = <Map<String, dynamic>>[];
      final apiClient = ApiClient(
        MockClient((request) async {
          requestedPaths.add(request.url.path);
          requestBodies.add(
            jsonDecode(request.body) as Map<String, dynamic>,
          );

          return http.Response(
            jsonEncode({
              'id': 42,
              'profile_id': 11,
              'date': '2026-06-18T00:00:00.000',
              'symptom': 'Bauchschmerzen',
              'bodyArea': 'Bauch',
              'intensity': 7,
              'note': 'Nach dem Essen',
              'createdAt': '2026-06-18T09:00:00.000',
            }),
            200,
            headers: {'content-type': 'application/json'},
          );
        }),
      );

      final service = SymptomApiService(apiClient);
      final response = await service.updateSymptom(
        profileId: 11,
        entryId: 42,
        date: DateTime(2026, 6, 18),
        symptom: 'Bauchschmerzen',
        bodyArea: 'Bauch',
        intensity: 7,
        note: 'Nach dem Essen',
      );

      expect(requestedPaths, ['/profiles/11/symptoms/42']);
      expect(requestBodies.single['symptom'], 'Bauchschmerzen');
      expect(requestBodies.single['bodyArea'], 'Bauch');
      expect(requestBodies.single['intensity'], 7);
      expect(response.id, 42);
      expect(response.symptom, 'Bauchschmerzen');
    });
  });
}
