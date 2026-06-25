import 'package:shared_preferences/shared_preferences.dart';

import 'medication_api_service.dart';
import 'medication_entry.dart';

/// Local storage adapter for user-managed medication entries.
class MedicationRepository {
  // Keep the legacy key so existing local medication entries stay available.
  static const _storageKey = 'medication_log_entries';

  final MedicationApiService? _apiService;
  final int? _profileId;

  const MedicationRepository({MedicationApiService? apiService, int? profileId})
    : _apiService = apiService,
      _profileId = profileId;

  /// Loads entries from SharedPreferences and sorts them by first intake time.
  Future<List<MedicationEntry>> loadEntries() async {
    final apiService = _apiService;
    final profileId = _profileId;

    if (apiService != null && profileId != null) {
      try {
        final entries = _sortedEntries(
          await apiService.getMedications(profileId),
        );
        await saveEntries(entries);
        return entries;
      } catch (_) {
        // Keep the cache readable, but do not implement offline write syncing yet.
        return _loadCachedEntries();
      }
    }

    return _loadCachedEntries();
  }

  /// Creates one entry remotely when configured, otherwise returns it unchanged.
  Future<MedicationEntry> createEntry(MedicationEntry entry) async {
    final apiService = _apiService;
    final profileId = _profileId;

    if (apiService == null || profileId == null) {
      return entry;
    }

    return apiService.createMedication(profileId, entry);
  }

  /// Updates one entry remotely when configured, otherwise returns it unchanged.
  Future<MedicationEntry> updateEntry(MedicationEntry entry) async {
    final apiService = _apiService;
    final profileId = _profileId;

    if (apiService == null || profileId == null) {
      return entry;
    }

    return apiService.updateMedication(profileId, entry);
  }

  /// Deletes one entry remotely when configured.
  Future<void> deleteEntry(MedicationEntry entry) async {
    final apiService = _apiService;
    final profileId = _profileId;

    if (apiService == null || profileId == null) {
      return;
    }

    await apiService.deleteMedication(profileId, entry.id);
  }

  /// Replaces the locally cached medication list.
  Future<void> saveEntries(List<MedicationEntry> entries) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setStringList(
      _currentStorageKey,
      entries.map((entry) => entry.encode()).toList(),
    );
  }

  Future<List<MedicationEntry>> _loadCachedEntries() async {
    final prefs = await SharedPreferences.getInstance();
    final encodedEntries = prefs.getStringList(_currentStorageKey) ?? const [];

    return _sortedEntries(encodedEntries.map(MedicationEntry.decode).toList());
  }

  List<MedicationEntry> _sortedEntries(List<MedicationEntry> entries) {
    return entries..sort((a, b) {
      final aMinutes = a.intakeTime.hour * 60 + a.intakeTime.minute;
      final bMinutes = b.intakeTime.hour * 60 + b.intakeTime.minute;
      return aMinutes.compareTo(bMinutes);
    });
  }

  String get _currentStorageKey =>
      _profileId == null ? _storageKey : '${_storageKey}_profile_$_profileId';
}
