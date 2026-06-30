import '../../../core/network/api_exception.dart';
import 'symptom_api_service.dart';
import 'symptom_entry.dart';
import 'symptom_repository.dart';

/// Loads symptom diary entries from the backend into local storage.
class SymptomSyncService {
  final SymptomApiService _apiService;
  final SymptomRepository _repository;

  SymptomSyncService(this._apiService, {SymptomRepository? repository})
    : _repository = repository ?? SymptomRepository();

  /// Flushes offline changes and refreshes the cache for [profileId].
  Future<void> syncActiveProfile(int profileId) async {
    final localEntries = await _repository.loadEntries(profileId: profileId);
    final pendingDeleteIds = await _repository.loadPendingDeleteIds(
      profileId: profileId,
    );

    for (final entryId in pendingDeleteIds.toList()) {
      try {
        await _apiService.deleteSymptom(profileId: profileId, entryId: entryId);
        await _repository.removePendingDelete(
          profileId: profileId,
          entryId: entryId,
        );
      } on ApiException catch (error) {
        if (error.statusCode == 404) {
          await _repository.removePendingDelete(
            profileId: profileId,
            entryId: entryId,
          );
        }
      } catch (_) {
        // Keep the deletion queued for the next synchronization attempt.
      }
    }

    final processedEntries = <SymptomEntry>[];
    for (final entry in localEntries) {
      try {
        if (!entry.isSynced) {
          final response = await _apiService.createSymptom(
            profileId: profileId,
            date: entry.date,
            symptom: entry.symptom,
            bodyArea: entry.bodyArea,
            intensity: entry.intensity,
            temperatureC: entry.temperatureC,
            note: entry.note,
            source: entry.source,
            createdAt: entry.createdAt,
          );
          processedEntries.add(SymptomEntry.fromResponse(response));
          continue;
        }

        if (entry.pendingUpdate) {
          final response = await _apiService.updateSymptom(
            profileId: profileId,
            entryId: entry.id,
            date: entry.date,
            symptom: entry.symptom,
            bodyArea: entry.bodyArea,
            intensity: entry.intensity,
            temperatureC: entry.temperatureC,
            note: entry.note,
          );
          processedEntries.add(SymptomEntry.fromResponse(response));
          continue;
        }

        processedEntries.add(entry);
      } catch (_) {
        processedEntries.add(entry);
      }
    }

    await _repository.saveEntries(
      profileId: profileId,
      entries: processedEntries,
    );

    final remoteEntries = (await _apiService.getSymptoms(
      profileId: profileId,
    )).map(SymptomEntry.fromResponse);
    final stillPendingDeletes = await _repository.loadPendingDeleteIds(
      profileId: profileId,
    );
    final mergedById = <int, SymptomEntry>{
      for (final entry in remoteEntries)
        if (!stillPendingDeletes.contains(entry.id)) entry.id: entry,
    };

    for (final entry in processedEntries) {
      if (!entry.isSynced || entry.pendingUpdate) {
        mergedById[entry.id] = entry;
      }
    }

    await _repository.saveEntries(
      profileId: profileId,
      entries: mergedById.values.toList(),
    );
  }
}
