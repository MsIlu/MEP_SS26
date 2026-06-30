import 'package:shared_preferences/shared_preferences.dart';

import 'symptom_entry.dart';

/// Local storage adapter for daily symptom diary entries.
class SymptomRepository {
  static const _storageKeyPrefix = 'symptom_diary_entries_profile_';

  String _storageKey(int profileId) => '$_storageKeyPrefix$profileId';

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
  }
}
