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
        await repository.saveEntries(
          profileId: 10,
          entries: [
            SymptomEntry(
              id: 10,
              date: DateTime(2026, 6, 17),
              symptom: 'Alter Profil-Cache',
              intensity: 5,
              note: 'Darf nach Profilwechsel nicht bleiben',
              createdAt: DateTime(2026, 6, 17, 8),
            ),
          ],
        );

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

        final entries = await repository.loadEntries(profileId: 11);
        expect(requestedPaths, ['/profiles/11/symptoms']);
        expect(entries, hasLength(1));
        expect(entries.single.id, 42);
        expect(entries.single.symptom, 'Neues Profil aus DB');
        expect(entries.single.isSynced, isTrue);
        expect(
          entries.map((entry) => entry.symptom),
          isNot(contains('Alter Profil-Cache')),
        );
        final previousProfileEntries = await repository.loadEntries(
          profileId: 10,
        );
        expect(previousProfileEntries.single.symptom, 'Alter Profil-Cache');
      },
    );

    test('uploads an offline entry before refreshing the profile', () async {
      final repository = SymptomRepository();
      await repository.saveEntries(
        profileId: 11,
        entries: [
          SymptomEntry(
            id: 999,
            date: DateTime(2026, 6, 20),
            symptom: 'Fieber',
            intensity: 6,
            temperatureC: 38.7,
            note: '',
            source: 'careena',
            createdAt: DateTime(2026, 6, 20, 9),
          ),
        ],
      );

      final methods = <String>[];
      final responseEntry = {
        'id': 77,
        'profile_id': 11,
        'date': '2026-06-20T00:00:00.000',
        'symptom': 'Fieber',
        'bodyArea': '',
        'intensity': 6,
        'temperatureC': 38.7,
        'note': '',
        'source': 'careena',
        'createdAt': '2026-06-20T09:00:00.000',
        'updatedAt': '2026-06-20T09:00:00.000',
      };
      final apiClient = ApiClient(
        MockClient((request) async {
          methods.add(request.method);
          return http.Response(
            jsonEncode(
              request.method == 'POST' ? responseEntry : [responseEntry],
            ),
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

      final entries = await repository.loadEntries(profileId: 11);
      expect(methods, ['POST', 'GET']);
      expect(entries.single.id, 77);
      expect(entries.single.isSynced, isTrue);
      expect(entries.single.source, 'careena');
      expect(entries.single.temperatureC, 38.7);
    });
  });
}
