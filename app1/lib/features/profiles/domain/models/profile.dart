// Created as part of the MEP26 authentication and profile management implementation.
// Defines the frontend model for medical profiles.

class Profile {
  /// Medical profile data returned by the backend.
  final int id;
  final String displayName;
  final String? dateOfBirth;
  final String? biologicalSex;
  final String profileType;
  final String? relevantPreconditionsSummary;
  final String? relevantMedicationsSummary;
  final String? symptomDiarySummary;
  final String? role;

  const Profile({
    required this.id,
    required this.displayName,
    this.dateOfBirth,
    this.biologicalSex,
    required this.profileType,
    this.relevantPreconditionsSummary,
    this.relevantMedicationsSummary,
    this.symptomDiarySummary,
    this.role,
  });

  factory Profile.fromJson(Map<String, dynamic> json) {
    return Profile(
      id: json['id'] as int,
      displayName: json['display_name'] as String,
      dateOfBirth: json['date_of_birth'] as String?,
      biologicalSex: json['biological_sex'] as String?,
      profileType: json['profile_type'] as String,
      relevantPreconditionsSummary:
      json['relevant_preconditions_summary'] as String?,
      relevantMedicationsSummary:
      json['relevant_medications_summary'] as String?,
      symptomDiarySummary: json['symptom_diary_summary'] as String?,
      role: json['role'] as String?,
    );
  }
}