import 'dart:convert';

import 'package:app1/core/network/api_client.dart';
import 'package:app1/features/recommendation_export/data/appointment_search_api_service.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

void main() {
  group('AppointmentSearchApiService', () {
    test('search parses HAPI FHIR appointment results', () async {
      final mockHttpClient = MockClient((request) async {
        expect(request.method, 'POST');
        expect(request.url.path, contains('/appointments/search'));

        final body = jsonDecode(request.body) as Map<String, dynamic>;
        expect(body['session_id'], 'session-1');
        expect(body['profile_id'], 10);
        expect(body['postal_code'], '68159');

        return http.Response(
          jsonEncode({
            'session_id': 'session-1',
            'profile_id': 10,
            'postal_code': '68159',
            'message': 'HAPI-FHIR hat Termine bereitgestellt.',
            'appointments': [
              {
                'id': 'hapi-appointment-1',
                'provider_name': 'Hausarztpraxis Dr. Schneider',
                'specialty': 'Allgemeinmedizin',
                'address': 'Musterstrasse 12, 68159 Mannheim',
                'distance_km': 2.4,
                'date': '2026-07-02',
                'time': '09:30',
                'care_type': 'Vor-Ort-Termin',
                'urgency_match': true,
                'source': 'hapi-fhir',
              },
            ],
          }),
          200,
          headers: {'content-type': 'application/json'},
        );
      });

      final service = AppointmentSearchApiService(ApiClient(mockHttpClient));
      final response = await service.search(
        sessionId: 'session-1',
        profileId: 10,
        postalCode: '68159',
      );

      expect(response.appointments, hasLength(1));
      expect(response.appointments.first.id, 'hapi-appointment-1');
      expect(response.appointments.first.source, 'hapi-fhir');
      expect(response.appointments.first.appointmentDate, isNotNull);
    });

    test(
      'saveRecommendedAppointment posts profile-scoped FHIR appointment',
      () async {
        Map<String, dynamic>? sentBody;

        final mockHttpClient = MockClient((request) async {
          expect(request.method, 'POST');
          expect(
            request.url.path,
            contains('/profiles/10/appointments/recommended'),
          );

          sentBody = jsonDecode(request.body) as Map<String, dynamic>;

          return http.Response(
            jsonEncode({
              'id': 7,
              'profile_id': 10,
              'session_id': 'session-1',
              'fhir_appointment_id': 'hapi-appointment-1',
              'provider_name': 'Hausarztpraxis Dr. Schneider',
              'specialty': 'Allgemeinmedizin',
              'address': 'Musterstrasse 12, 68159 Mannheim',
              'distance_km': 2.4,
              'starts_at': '2026-07-02T09:30:00',
              'care_type': 'Vor-Ort-Termin',
              'note': 'Von Careena empfohlen',
              'created_at': '2026-07-01T08:00:00',
              'updated_at': '2026-07-01T08:00:00',
            }),
            200,
            headers: {'content-type': 'application/json'},
          );
        });

        final service = AppointmentSearchApiService(ApiClient(mockHttpClient));
        await service.saveRecommendedAppointment(
          profileId: 10,
          sessionId: 'session-1',
          note: 'Von Careena empfohlen',
          appointment: FhirAppointmentResult(
            id: 'hapi-appointment-1',
            providerName: 'Hausarztpraxis Dr. Schneider',
            specialty: 'Allgemeinmedizin',
            address: 'Musterstrasse 12, 68159 Mannheim',
            distanceKm: 2.4,
            date: '2026-07-02',
            time: '09:30',
            careType: 'Vor-Ort-Termin',
            urgencyMatch: true,
            source: 'hapi-fhir',
          ),
        );

        expect(sentBody?['session_id'], 'session-1');
        expect(sentBody?['fhir_appointment_id'], 'hapi-appointment-1');
        expect(sentBody?['provider_name'], 'Hausarztpraxis Dr. Schneider');
        expect(sentBody?['date'], '2026-07-02');
        expect(sentBody?['time'], '09:30');
      },
    );
  });
}
