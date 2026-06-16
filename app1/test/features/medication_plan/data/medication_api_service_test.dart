import 'dart:convert';

import 'package:app1/core/network/api_client.dart';
import 'package:app1/features/medication_plan/data/medication_api_service.dart';
import 'package:app1/features/medication_plan/data/medication_catalog_item.dart';
import 'package:app1/features/medication_plan/data/medication_entry.dart';
import 'package:app1/features/medication_plan/data/medication_schedule.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

void main() {
  group('MedicationApiService', () {
    test(
      'getMedications parses medication list and sends auth header',
      () async {
        String? authorizationHeader;

        final mockHttpClient = MockClient((request) async {
          expect(request.method, 'GET');
          expect(request.url.path, contains('/profiles/10/medications'));

          authorizationHeader = request.headers['Authorization'];

          return http.Response(
            jsonEncode([_apiMedicationJson()]),
            200,
            headers: {'content-type': 'application/json'},
          );
        });

        final apiClient = ApiClient(mockHttpClient);
        apiClient.setAccessToken('test-token');

        final service = MedicationApiService(apiClient);
        final medications = await service.getMedications(10);

        expect(authorizationHeader, 'Bearer test-token');
        expect(medications, hasLength(1));
        expect(medications.first.id, 42);
        expect(medications.first.name, 'Ibuprofen');
        expect(medications.first.frequency, MedicationFrequency.twiceDaily);
        expect(
          medications.first.secondIntakeTime,
          const TimeOfDay(hour: 20, minute: 0),
        );
        expect(medications.first.catalogItem?.activeSubstance, 'Ibuprofen');
      },
    );

    test('createMedication sends FastAPI medication JSON', () async {
      Map<String, dynamic>? sentBody;

      final mockHttpClient = MockClient((request) async {
        expect(request.method, 'POST');
        expect(request.url.path, contains('/profiles/10/medications'));

        sentBody = jsonDecode(request.body) as Map<String, dynamic>;

        return http.Response(
          jsonEncode(_apiMedicationJson(id: 43)),
          200,
          headers: {'content-type': 'application/json'},
        );
      });

      final service = MedicationApiService(ApiClient(mockHttpClient));
      final created = await service.createMedication(10, _entry());

      expect(sentBody?['name'], 'Ibuprofen');
      expect(sentBody?['dose'], '400 mg');
      expect(sentBody?['intake_hour'], 8);
      expect(sentBody?['intake_minute'], 30);
      expect(sentBody?['second_intake_hour'], 20);
      expect(sentBody?['second_intake_minute'], 0);
      expect(sentBody?['frequency'], 'twice_daily');
      expect(sentBody?['reminders_enabled'], true);
      expect(sentBody?['taken_date_keys'], ['2026-06-12:0']);
      expect(sentBody?['catalog_item']['active_substance'], 'Ibuprofen');

      expect(created.id, 43);
    });

    test('updateMedication sends patch JSON without createdAt', () async {
      Map<String, dynamic>? sentBody;

      final mockHttpClient = MockClient((request) async {
        expect(request.method, 'PATCH');
        expect(request.url.path, contains('/profiles/10/medications/1'));

        sentBody = jsonDecode(request.body) as Map<String, dynamic>;

        return http.Response(
          jsonEncode(_apiMedicationJson()),
          200,
          headers: {'content-type': 'application/json'},
        );
      });

      final service = MedicationApiService(ApiClient(mockHttpClient));
      await service.updateMedication(10, _entry());

      expect(sentBody, isNot(contains('created_at')));
      expect(sentBody?['name'], 'Ibuprofen');
      expect(sentBody?['taken_date_keys'], ['2026-06-12:0']);
    });
  });
}

MedicationEntry _entry() {
  return MedicationEntry(
    id: 1,
    name: 'Ibuprofen',
    dose: '400 mg',
    intakeTime: const TimeOfDay(hour: 8, minute: 30),
    secondIntakeTime: const TimeOfDay(hour: 20, minute: 0),
    frequency: MedicationFrequency.twiceDaily,
    remindersEnabled: true,
    createdAt: DateTime(2026, 6, 12),
    takenDateKeys: const ['2026-06-12:0'],
    catalogItem: const MedicationCatalogItem(
      id: 'demo-ibuprofen',
      name: 'Ibuprofen 400 mg',
      activeSubstance: 'Ibuprofen',
      strength: '400 mg',
      dosageForm: 'Tablette',
    ),
  );
}

Map<String, dynamic> _apiMedicationJson({int id = 42}) {
  return {
    'id': id,
    'profile_id': 10,
    'name': 'Ibuprofen',
    'dose': '400 mg',
    'intake_hour': 8,
    'intake_minute': 30,
    'second_intake_hour': 20,
    'second_intake_minute': 0,
    'frequency': 'twice_daily',
    'reminders_enabled': true,
    'taken_date_keys': ['2026-06-12:0'],
    'catalog_item': {
      'id': 'demo-ibuprofen',
      'name': 'Ibuprofen 400 mg',
      'active_substance': 'Ibuprofen',
      'strength': '400 mg',
      'dosage_form': 'Tablette',
    },
    'created_at': '2026-06-12T08:00:00',
    'updated_at': '2026-06-12T09:00:00',
  };
}
