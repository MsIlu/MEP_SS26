import 'package:shared_preferences/shared_preferences.dart';

import 'symptom_entry.dart';

/// Local storage adapter for daily symptom diary entries.
class SymptomRepository {
  static const _storageKeyPrefix = 'symptom_diary_entries_profile_';
  static const _pendingDeletesKeyPrefix =
      'symptom_diary_pending_deletes_profile_';

  String _storageKey(int profileId) => '$_storageKeyPrefix$profileId';
  String _pendingDeletesKey(int profileId) =>
      '$_pendingDeletesKeyPrefix$profileId';

  /// Loads entries and orders the newest day first for history views.
  Future<List<SymptomEntry>> loadEntries({required int profileId}) async {
    final prefs = await SharedPreferences.getInstance();
    final encodedEntries =
        prefs.getStringList(_storageKey(profileId)) ?? const [];

    return encodedEntries.map(SymptomEntry.decode).toList()
      ..sort((a, b) => b.date.compareTo(a.date));
  }

  /// Replaces the locally stored diary entries.
  Future<void> saveEntries({
    required int profileId,
    required List<SymptomEntry> entries,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setStringList(
      _storageKey(profileId),
      entries.map((entry) => entry.encode()).toList(),
    );
  }

  /// Removes all locally stored symptom diary entries.
  Future<void> clearEntries({required int profileId}) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_storageKey(profileId));
    await prefs.remove(_pendingDeletesKey(profileId));
  }

  Future<Set<int>> loadPendingDeleteIds({required int profileId}) async {
    final prefs = await SharedPreferences.getInstance();
    final values =
        prefs.getStringList(_pendingDeletesKey(profileId)) ?? const [];
    return values.map(int.tryParse).whereType<int>().toSet();
  }

  Future<void> addPendingDelete({
    required int profileId,
    required int entryId,
  }) async {
    final ids = await loadPendingDeleteIds(profileId: profileId);
    ids.add(entryId);
    await _savePendingDeleteIds(profileId, ids);
  }

  Future<void> removePendingDelete({
    required int profileId,
    required int entryId,
  }) async {
    final ids = await loadPendingDeleteIds(profileId: profileId);
    ids.remove(entryId);
    await _savePendingDeleteIds(profileId, ids);
  }

  Future<void> _savePendingDeleteIds(int profileId, Set<int> ids) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setStringList(
      _pendingDeletesKey(profileId),
      ids.map((id) => id.toString()).toList()..sort(),
    );
  }
}
