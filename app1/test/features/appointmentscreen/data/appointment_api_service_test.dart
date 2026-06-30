import 'dart:convert';

import 'package:app1/core/network/api_client.dart';
import 'package:app1/features/appointmentscreen/data/appointment_api_service.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

void main() {
  group('AppointmentApiService', () {
    test('loads recommended DB appointments for a profile', () async {
      final mockHttpClient = MockClient((request) async {
        expect(request.method, 'GET');
        expect(
          request.url.path,
          contains('/profiles/10/appointments/recommended'),
        );

        return http.Response(
          jsonEncode([
            {
              'id': 7,
              'profile_id': 10,
              'booked_by_account_id': 3,
              'session_id': 'session-1',
              'fhir_appointment_id': 'hapi-appointment-1',
              'provider_name': 'Hausarztpraxis Dr. Schneider',
              'specialty': 'Allgemeinmedizin',
              'address': 'Musterstrasse 12, 68159 Mannheim',
              'distance_km': 2.4,
              'starts_at': '2026-07-02T09:30:00',
              'care_type': 'Vor-Ort-Termin',
              'note': null,
              'status': 'booked',
              'created_at': '2026-07-01T08:00:00',
              'updated_at': '2026-07-01T08:00:00',
            },
          ]),
          200,
          headers: {'content-type': 'application/json'},
        );
      });

      final service = AppointmentApiService(ApiClient(mockHttpClient));

      final appointments = await service.getRecommendedAppointments(
        profileId: 10,
      );

      expect(appointments, hasLength(1));
      expect(appointments.first.id, 'hapi-appointment-1');
      expect(appointments.first.profileId, 10);
      expect(appointments.first.doctorName, 'Hausarztpraxis Dr. Schneider');
      expect(appointments.first.appointmentDate, DateTime(2026, 7, 2, 9, 30));
      expect(appointments.first.note, contains('Musterstrasse 12'));
      expect(appointments.first.isRecommendation, isTrue);
    });
  });
}
