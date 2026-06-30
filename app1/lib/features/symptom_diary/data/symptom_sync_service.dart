import 'symptom_api_service.dart';
import 'symptom_entry.dart';
import 'symptom_repository.dart';

/// Loads symptom diary entries from the backend into local storage.
class SymptomSyncService {
  final SymptomApiService _apiService;
  final SymptomRepository _repository;

  SymptomSyncService(this._apiService, {SymptomRepository? repository})
    : _repository = repository ?? SymptomRepository();

  /// Fetches all symptom entries for [profileId] and replaces the local cache.
  Future<void> syncActiveProfile(int profileId) async {
    final remoteEntries = await _apiService.getSymptoms(profileId: profileId);
    final entries = remoteEntries.map(SymptomEntry.fromResponse).toList();

    await _repository.saveEntries(profileId: profileId, entries: entries);
  }
}
