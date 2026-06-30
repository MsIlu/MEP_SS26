import 'package:app1/core/network/api_client.dart';

class AppointmentSearchApiService {
  final ApiClient client;

  AppointmentSearchApiService(this.client);

  Future<AppointmentSearchResponse> search({
    required String sessionId,
    required int profileId,
    required String postalCode,
  }) async {
    final data = await client.post('/appointments/search', {
      'session_id': sessionId,
      'profile_id': profileId,
      'postal_code': postalCode,
    });

    return AppointmentSearchResponse.fromJson(data);
  }
}

class AppointmentSearchResponse {
  final String sessionId;
  final int profileId;
  final String postalCode;
  final String message;
  final List<SimulatedAppointmentResult> appointments;

  AppointmentSearchResponse({
    required this.sessionId,
    required this.profileId,
    required this.postalCode,
    required this.message,
    required this.appointments,
  });

  factory AppointmentSearchResponse.fromJson(Map<String, dynamic> json) {
    return AppointmentSearchResponse(
      sessionId: json['session_id']?.toString() ?? '',
      profileId: json['profile_id'] as int,
      postalCode: json['postal_code']?.toString() ?? '',
      message: json['message']?.toString() ?? '',
      appointments: (json['appointments'] as List<dynamic>? ?? [])
          .whereType<Map<String, dynamic>>()
          .map(SimulatedAppointmentResult.fromJson)
          .toList(),
    );
  }
}

class SimulatedAppointmentResult {
  final String id;
  final String providerName;
  final String specialty;
  final String address;
  final double distanceKm;
  final String date;
  final String time;
  final String careType;
  final bool urgencyMatch;

  SimulatedAppointmentResult({
    required this.id,
    required this.providerName,
    required this.specialty,
    required this.address,
    required this.distanceKm,
    required this.date,
    required this.time,
    required this.careType,
    required this.urgencyMatch,
  });

  factory SimulatedAppointmentResult.fromJson(Map<String, dynamic> json) {
    return SimulatedAppointmentResult(
      id: json['id']?.toString() ?? '',
      providerName: json['provider_name']?.toString() ?? '',
      specialty: json['specialty']?.toString() ?? '',
      address: json['address']?.toString() ?? '',
      distanceKm: (json['distance_km'] as num?)?.toDouble() ?? 0,
      date: json['date']?.toString() ?? '',
      time: json['time']?.toString() ?? '',
      careType: json['care_type']?.toString() ?? '',
      urgencyMatch: json['urgency_match'] == true,
    );
  }

  DateTime? get appointmentDate {
    return DateTime.tryParse('${date}T$time:00');
  }
}