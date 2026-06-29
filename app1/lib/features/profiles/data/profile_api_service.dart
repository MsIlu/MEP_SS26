// Created as part of the MEP26 authentication and profile management implementation.
// Provides API methods for loading, creating, updating, and deleting profiles.

import '../../../core/network/api_client.dart';
import '../domain/models/profile.dart';

class ProfileApiService {
  /// API client used to communicate with the backend.
  final ApiClient _apiClient;

  const ProfileApiService(this._apiClient);

  /// Loads all profiles accessible by the authenticated account.
  Future<List<Profile>> getProfiles() async {
    final response = await _apiClient.getList('/profiles');

    return response
        .map((item) => Profile.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  /// Loads a single profile by id.
  Future<Profile> getProfile(int profileId) async {
    final response = await _apiClient.get('/profiles/$profileId');
    return Profile.fromJson(response);
  }

  /// Creates a new profile for the authenticated account.
  Future<Profile> createProfile({
    required String displayName,
    String? dateOfBirth,
    String? biologicalSex,
    int? heightCm,
    double? weightKg,
    String profileType = 'other',
    String? relevantPreconditionsSummary,
    String? relevantMedicationsSummary,
    String? symptomDiarySummary,
    String? aiDisclaimerAcceptedAt,
  }) async {
    final response = await _apiClient.post('/profiles', {
      'display_name': displayName,
      'date_of_birth': dateOfBirth,
      'biological_sex': biologicalSex,
      'height_cm': heightCm,
      'weight_kg': weightKg,
      'profile_type': profileType,
      'relevant_preconditions_summary': relevantPreconditionsSummary,
      'relevant_medications_summary': relevantMedicationsSummary,
      'symptom_diary_summary': symptomDiarySummary,
      'ai_disclaimer_accepted_at': aiDisclaimerAcceptedAt,
    });

    return Profile.fromJson(response);
  }

  /// Updates an existing profile.
  Future<Profile> updateProfile({
    required int profileId,
    String? displayName,
    String? dateOfBirth,
    String? biologicalSex,
    int? heightCm,
    double? weightKg,
    String? profileType,
    String? relevantPreconditionsSummary,
    String? relevantMedicationsSummary,
    String? symptomDiarySummary,
    String? aiDisclaimerAcceptedAt,
  }) async {
    final body = <String, dynamic>{};

    if (displayName != null) {
      body['display_name'] = displayName;
    }
    if (dateOfBirth != null) {
      body['date_of_birth'] = dateOfBirth;
    }
    if (biologicalSex != null) {
      body['biological_sex'] = biologicalSex;
    }
    if (heightCm != null) {
      body['height_cm'] = heightCm;
    }
    if (weightKg != null) {
      body['weight_kg'] = weightKg;
    }
    if (profileType != null) {
      body['profile_type'] = profileType;
    }
    if (relevantPreconditionsSummary != null) {
      body['relevant_preconditions_summary'] = relevantPreconditionsSummary;
    }
    if (relevantMedicationsSummary != null) {
      body['relevant_medications_summary'] = relevantMedicationsSummary;
    }
    if (symptomDiarySummary != null) {
      body['symptom_diary_summary'] = symptomDiarySummary;
    }
    if (aiDisclaimerAcceptedAt != null) {
      body['ai_disclaimer_accepted_at'] = aiDisclaimerAcceptedAt;
    }

    final response = await _apiClient.patch('/profiles/$profileId', body);
    return Profile.fromJson(response);
  }

  Future<Profile> updateProfileFields({
    required int profileId,
    required Map<String, dynamic> fields,
  }) async {
    final response = await _apiClient.patch('/profiles/$profileId', fields);
    return Profile.fromJson(response);
  }

  /// Soft-deletes a profile.
  Future<void> deleteProfile(int profileId) async {
    await _apiClient.delete('/profiles/$profileId');
  }
}
