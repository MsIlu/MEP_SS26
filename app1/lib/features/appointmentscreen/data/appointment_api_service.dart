import 'package:app1/core/network/api_client.dart';

import 'models/appointment.dart';

class AppointmentApiService {
  final ApiClient client;

  AppointmentApiService(this.client);

  Future<List<Appointment>> getRecommendedAppointments({
    required int profileId,
  }) async {
    final data = await client.getList(
      '/profiles/$profileId/appointments/recommended',
    );

    return data
        .whereType<Map<String, dynamic>>()
        .map(RecommendedAppointmentResult.fromJson)
        .map((appointment) => appointment.toAppointment())
        .toList();
  }

  Future<void> cancelRecommendedAppointment({
    required int profileId,
    required int appointmentId,
  }) async {
    await client.delete(
      '/profiles/$profileId/appointments/recommended/$appointmentId',
    );
  }

  Future<Appointment> rescheduleRecommendedAppointment({
    required int profileId,
    required int appointmentId,
    required String sessionId,
    required String replacementFhirAppointmentId,
    String? note,
  }) async {
    final data = await client.patch(
      '/profiles/$profileId/appointments/recommended/$appointmentId/reschedule',
      {
        'session_id': sessionId,
        'replacement_fhir_appointment_id': replacementFhirAppointmentId,
        'note': ?note,
      },
    );
    return RecommendedAppointmentResult.fromJson(data).toAppointment();
  }
}

class RecommendedAppointmentResult {
  final int id;
  final int profileId;
  final int? bookedByAccountId;
  final String? sessionId;
  final String fhirAppointmentId;
  final String providerName;
  final String specialty;
  final String address;
  final double distanceKm;
  final DateTime? startsAt;
  final String careType;
  final String? note;
  final String status;

  RecommendedAppointmentResult({
    required this.id,
    required this.profileId,
    required this.bookedByAccountId,
    required this.sessionId,
    required this.fhirAppointmentId,
    required this.providerName,
    required this.specialty,
    required this.address,
    required this.distanceKm,
    required this.startsAt,
    required this.careType,
    required this.note,
    required this.status,
  });

  factory RecommendedAppointmentResult.fromJson(Map<String, dynamic> json) {
    return RecommendedAppointmentResult(
      id: _intFromJson(json['id']) ?? 0,
      profileId: _intFromJson(json['profile_id']) ?? 0,
      bookedByAccountId: _intFromJson(json['booked_by_account_id']),
      sessionId: json['session_id']?.toString(),
      fhirAppointmentId: json['fhir_appointment_id']?.toString() ?? '',
      providerName: json['provider_name']?.toString() ?? '',
      specialty: json['specialty']?.toString() ?? '',
      address: json['address']?.toString() ?? '',
      distanceKm: (json['distance_km'] as num?)?.toDouble() ?? 0,
      startsAt: DateTime.tryParse(json['starts_at']?.toString() ?? ''),
      careType: json['care_type']?.toString() ?? '',
      note: json['note']?.toString(),
      status: json['status']?.toString() ?? 'booked',
    );
  }

  Appointment toAppointment() {
    return Appointment(
      id: fhirAppointmentId.isNotEmpty ? fhirAppointmentId : id.toString(),
      backendId: id,
      profileId: profileId,
      sessionId: sessionId,
      doctorName: providerName,
      appointmentDate: startsAt,
      note: _displayNote,
      isRecommendation: true,
    );
  }

  String get _displayNote {
    final trimmedNote = note?.trim();
    if (trimmedNote != null && trimmedNote.isNotEmpty) {
      return trimmedNote;
    }

    final details = <String>[
      'Von Careena empfohlen',
      if (specialty.isNotEmpty) 'Fachrichtung: $specialty',
      if (careType.isNotEmpty) 'Versorgungsart: $careType',
      if (address.isNotEmpty) 'Adresse: $address',
      if (distanceKm > 0) 'Entfernung: ${distanceKm.toStringAsFixed(1)} km',
      if (status.isNotEmpty) 'Status: $status',
    ];

    return details.join('\n');
  }
}

int? _intFromJson(dynamic value) {
  if (value is int) return value;
  if (value is num) return value.toInt();
  return int.tryParse(value?.toString() ?? '');
}
