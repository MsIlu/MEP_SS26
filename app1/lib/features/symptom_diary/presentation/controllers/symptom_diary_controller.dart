import 'package:flutter/foundation.dart';

import '../../data/symptom_entry.dart';
import '../../data/symptom_repository.dart';
import '../utils/symptom_date_format.dart';

/// Coordinates symptom diary state, local persistence, and derived summaries.
class SymptomDiaryController extends ChangeNotifier {
  final SymptomRepository _repository;

  SymptomDiaryController({SymptomRepository? repository})
    : _repository = repository ?? SymptomRepository();

  final List<SymptomEntry> _entries = [];
  bool _isLoading = true;

  List<SymptomEntry> get entries => List.unmodifiable(_entries);
  bool get isLoading => _isLoading;

  /// Loads locally persisted diary entries once the page starts.
  Future<void> loadEntries() async {
    _isLoading = true;
    notifyListeners();

    final loadedEntries = await _repository.loadEntries();
    _entries
      ..clear()
      ..addAll(loadedEntries);

    _isLoading = false;
    notifyListeners();
  }

  /// Adds one symptom record for the selected calendar day.
  Future<void> addEntry({
    required DateTime date,
    required String symptom,
    String bodyArea = '',
    required int intensity,
    required String note,
  }) async {
    final normalizedSymptom = symptom.trim();
    if (normalizedSymptom.isEmpty) {
      return;
    }

    final now = DateTime.now();
    _entries.add(
      SymptomEntry(
        id: now.microsecondsSinceEpoch,
        date: DateTime(date.year, date.month, date.day),
        symptom: normalizedSymptom,
        bodyArea: bodyArea.trim(),
        intensity: intensity.clamp(1, 10),
        note: note.trim(),
        createdAt: now,
      ),
    );
    _sortEntries();
    await _saveAndNotify();
  }

  /// Removes an entry without touching other days.
  Future<void> deleteEntry(SymptomEntry entry) async {
    _entries.removeWhere((item) => item.id == entry.id);
    await _saveAndNotify();
  }

  /// Returns all entries for one calendar day in creation order.
  List<SymptomEntry> entriesForDate(DateTime date) {
    return _entries
        .where((entry) => isSameSymptomDay(entry.date, date))
        .toList()
      ..sort((a, b) => a.createdAt.compareTo(b.createdAt));
  }

  /// Calculates the average intensity for the selected day.
  double averageIntensityForDate(DateTime date) {
    final dayEntries = entriesForDate(date);
    if (dayEntries.isEmpty) {
      return 0;
    }

    final total = dayEntries.fold<int>(
      0,
      (sum, entry) => sum + entry.intensity,
    );
    return total / dayEntries.length;
  }

  void _sortEntries() {
    _entries.sort((a, b) {
      final dayComparison = b.date.compareTo(a.date);
      if (dayComparison != 0) {
        return dayComparison;
      }
      return b.createdAt.compareTo(a.createdAt);
    });
  }

  Future<void> _saveAndNotify() async {
    await _repository.saveEntries(_entries);
    notifyListeners();
  }
}