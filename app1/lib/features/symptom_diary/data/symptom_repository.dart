import 'package:shared_preferences/shared_preferences.dart';

import 'symptom_entry.dart';

/// Local storage adapter for daily symptom diary entries.
class SymptomRepository {
  static const _storageKey = 'symptom_diary_entries';

  /// Loads entries and orders the newest day first for history views.
  Future<List<SymptomEntry>> loadEntries() async {
    final prefs = await SharedPreferences.getInstance();
    final encodedEntries = prefs.getStringList(_storageKey) ?? const [];

    return encodedEntries.map(SymptomEntry.decode).toList()
      ..sort((a, b) => b.date.compareTo(a.date));
  }

  /// Replaces the locally stored diary entries.
  Future<void> saveEntries(List<SymptomEntry> entries) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setStringList(
      _storageKey,
      entries.map((entry) => entry.encode()).toList(),
    );
  }

  /// Merges server entries into local storage without dropping unsynced notes.
  Future<void> importServerEntries(List<SymptomEntry> serverEntries) async {
    final localEntries = await loadEntries();
    final mergedEntries = _mergeEntries(serverEntries, localEntries);

    await saveEntries(mergedEntries);
  }

  /// Removes all locally stored symptom diary entries.
  Future<void> clearEntries() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_storageKey);
  }

  List<SymptomEntry> _mergeEntries(
    List<SymptomEntry> serverEntries,
    List<SymptomEntry> localEntries,
  ) {
    final serverIds = serverEntries.map((entry) => entry.id).toSet();
    final unmatchedLocalEntries = localEntries.where((localEntry) {
      if (serverIds.contains(localEntry.id)) {
        return false;
      }

      return !serverEntries.any(
        (serverEntry) => _matchesEntry(localEntry, serverEntry),
      );
    });

    return [...serverEntries, ...unmatchedLocalEntries];
  }

  bool _matchesEntry(SymptomEntry first, SymptomEntry second) {
    return first.date.year == second.date.year &&
        first.date.month == second.date.month &&
        first.date.day == second.date.day &&
        first.symptom == second.symptom &&
        first.bodyArea == second.bodyArea &&
        first.intensity == second.intensity &&
        first.note == second.note;
  }
}
