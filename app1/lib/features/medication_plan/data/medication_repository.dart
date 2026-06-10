import 'package:shared_preferences/shared_preferences.dart';

import 'medication_entry.dart';

/// Local storage adapter for user-managed medication entries.
class MedicationRepository {
  // Keep the legacy key so existing local medication entries stay available.
  static const _storageKey = 'medication_log_entries';

  /// Loads entries from SharedPreferences and sorts them by first intake time.
  Future<List<MedicationEntry>> loadEntries() async {
    final prefs = await SharedPreferences.getInstance();
    final encodedEntries = prefs.getStringList(_storageKey) ?? const [];

    return encodedEntries.map(MedicationEntry.decode).toList()..sort((a, b) {
      final aMinutes = a.intakeTime.hour * 60 + a.intakeTime.minute;
      final bMinutes = b.intakeTime.hour * 60 + b.intakeTime.minute;
      return aMinutes.compareTo(bMinutes);
    });
  }

  /// Replaces the stored medication list with the latest controller state.
  Future<void> saveEntries(List<MedicationEntry> entries) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setStringList(
      _storageKey,
      entries.map((entry) => entry.encode()).toList(),
    );
  }
}