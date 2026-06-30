import 'package:flutter/foundation.dart';

import '../../../../core/network/api_exception.dart';
import '../../data/symptom_api_service.dart';
import '../../data/symptom_entry.dart';
import '../../data/symptom_repository.dart';
import '../utils/symptom_date_format.dart';

/// Coordinates symptom diary state, local persistence, and derived summaries.
class SymptomDiaryController extends ChangeNotifier {
  final SymptomRepository _repository;
  final SymptomApiService? _apiService;
  final int? _profileId;

  SymptomDiaryController({
    SymptomRepository? repository,
    SymptomApiService? apiService,
    int? profileId,
  }) : _repository = repository ?? SymptomRepository(),
       _apiService = apiService,
       _profileId = profileId;

  final List<SymptomEntry> _entries = [];
  bool _isLoading = true;

  List<SymptomEntry> get entries => List.unmodifiable(_entries);
  bool get isLoading => _isLoading;

  /// Loads locally persisted diary entries once the page starts.
  Future<void> loadEntries() async {
    _isLoading = true;
    notifyListeners();

    final profileId = _profileId;
    final loadedEntries = profileId == null
        ? <SymptomEntry>[]
        : await _repository.loadEntries(profileId: profileId);
    _entries
      ..clear()
      ..addAll(loadedEntries);

    _isLoading = false;
    notifyListeners();
  }

  /// Adds one symptom record for the selected calendar day.
  Future<SymptomEntry> addEntry({
    required DateTime date,
    required String symptom,
    String bodyArea = '',
    required int intensity,
    double? temperatureC,
    required String note,
    String source = 'manual',
  }) async {
    final normalizedSymptom = symptom.trim();
    if (normalizedSymptom.isEmpty) {
      throw ArgumentError('Symptom darf nicht leer sein.');
    }

    final now = DateTime.now();
    var entry = SymptomEntry(
      id: now.microsecondsSinceEpoch,
      date: DateTime(date.year, date.month, date.day),
      symptom: normalizedSymptom,
      bodyArea: bodyArea.trim(),
      intensity: intensity.clamp(1, 10),
      temperatureC: temperatureC,
      note: note.trim(),
      source: source,
      createdAt: now,
    );

    if (_profileId != null && _apiService != null) {
      try {
        final response = await _apiService.createSymptom(
          profileId: _profileId,
          date: entry.date,
          symptom: entry.symptom,
          bodyArea: entry.bodyArea,
          intensity: entry.intensity,
          temperatureC: entry.temperatureC,
          note: entry.note,
          source: entry.source,
          createdAt: entry.createdAt,
        );
        entry = SymptomEntry.fromResponse(response);
      } catch (error) {
        if (!_isOfflineError(error)) rethrow;
        // Keep the unsynced local entry for the next synchronization attempt.
      }
    }
    _entries.add(entry);
    _sortEntries();
    await _saveAndNotify();
    return entry;
  }

  /// Updates an existing entry locally and remotely when already synchronized.
  Future<SymptomEntry> updateEntry({
    required SymptomEntry entry,
    required DateTime date,
    required String symptom,
    required String bodyArea,
    required int intensity,
    double? temperatureC,
    required String note,
  }) async {
    final normalizedSymptom = symptom.trim();
    if (normalizedSymptom.isEmpty) {
      throw ArgumentError('Symptom darf nicht leer sein.');
    }

    var updatedEntry = entry.copyWith(
      date: DateTime(date.year, date.month, date.day),
      symptom: normalizedSymptom,
      bodyArea: bodyArea.trim(),
      intensity: intensity.clamp(1, 10),
      temperatureC: temperatureC,
      clearTemperature: temperatureC == null,
      note: note.trim(),
      updatedAt: DateTime.now(),
    );

    if (entry.isSynced && _profileId != null) {
      if (_apiService == null) {
        updatedEntry.pendingUpdate = true;
      } else {
        try {
          final response = await _apiService.updateSymptom(
            profileId: _profileId,
            entryId: entry.id,
            date: updatedEntry.date,
            symptom: updatedEntry.symptom,
            bodyArea: updatedEntry.bodyArea,
            intensity: updatedEntry.intensity,
            temperatureC: updatedEntry.temperatureC,
            note: updatedEntry.note,
          );
          updatedEntry = SymptomEntry.fromResponse(response);
        } catch (error) {
          if (!_isOfflineError(error)) rethrow;
          updatedEntry.pendingUpdate = true;
        }
      }
    }

    _entries
      ..removeWhere((item) => item.id == entry.id)
      ..add(updatedEntry);
    _sortEntries();
    await _saveAndNotify();
    return updatedEntry;
  }

  /// Removes an entry without touching other days.
  Future<void> deleteEntry(SymptomEntry entry) async {
    if (entry.isSynced && _profileId != null) {
      try {
        if (_apiService == null) throw StateError('API unavailable');
        await _apiService.deleteSymptom(
          profileId: _profileId,
          entryId: entry.id,
        );
      } catch (error) {
        if (!_isOfflineError(error) && error is! StateError) rethrow;
        await _repository.addPendingDelete(
          profileId: _profileId,
          entryId: entry.id,
        );
      }
    }

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
    final profileId = _profileId;
    if (profileId != null) {
      await _repository.saveEntries(profileId: profileId, entries: _entries);
    }
    notifyListeners();
  }

  bool _isOfflineError(Object error) {
    return error is ApiException &&
        (error.type == ApiErrorType.network ||
            error.type == ApiErrorType.timeout);
  }
}
