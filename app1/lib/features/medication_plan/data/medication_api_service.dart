// Provides API methods for profile-scoped medication entries.

import '../../../core/network/api_client.dart';
import 'medication_entry.dart';

class MedicationApiService {
  final ApiClient _apiClient;

  const MedicationApiService(this._apiClient);

  Future<List<MedicationEntry>> getMedications(int profileId) async {
    final response = await _apiClient.getList(_path(profileId));

    return response
        .map(
          (item) => MedicationEntry.fromApiJson(item as Map<String, dynamic>),
        )
        .toList();
  }

  Future<MedicationEntry> createMedication(
    int profileId,
    MedicationEntry entry,
  ) async {
    final response = await _apiClient.post(_path(profileId), entry.toApiJson());

    return MedicationEntry.fromApiJson(response);
  }

  Future<MedicationEntry> updateMedication(
    int profileId,
    MedicationEntry entry,
  ) async {
    final response = await _apiClient.patch(
      '${_path(profileId)}/${entry.id}',
      entry.toApiJson(includeCreatedAt: false),
    );

    return MedicationEntry.fromApiJson(response);
  }

  Future<void> deleteMedication(int profileId, int medicationId) async {
    await _apiClient.delete('${_path(profileId)}/$medicationId');
  }

  String _path(int profileId) => '/profiles/$profileId/medications';
}
