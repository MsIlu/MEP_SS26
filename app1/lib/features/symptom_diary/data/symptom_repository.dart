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
}