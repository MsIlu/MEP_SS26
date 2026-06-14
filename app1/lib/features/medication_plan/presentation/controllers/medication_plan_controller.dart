import 'package:flutter/material.dart';

import '../../data/medication_entry.dart';
import '../../data/medication_catalog_item.dart';
import '../../data/medication_repository.dart';
import '../../data/medication_schedule.dart';
import '../../services/medication_notification_service.dart';
import '../utils/medication_date_format.dart';

/// Coordinates medication plan persistence and reminder scheduling.
class MedicationPlanController extends ChangeNotifier {
  final MedicationRepository _repository;
  final MedicationNotificationService _notificationService;

  List<MedicationEntry> _entries = const [];
  bool _isLoading = true;
  bool _isDisposed = false;

  MedicationPlanController({
    MedicationRepository? repository,
    MedicationNotificationService? notificationService,
  }) : _repository = repository ?? MedicationRepository(),
       _notificationService =
           notificationService ?? MedicationNotificationService.instance;

  List<MedicationEntry> get entries => _entries;

  bool get isLoading => _isLoading;

  /// Loads persisted medication entries and presents them in intake order.
  Future<void> loadEntries() async {
    _entries = await _repository.loadEntries();
    await _syncTodayReminders();
    _isLoading = false;
    _notifyIfActive();
  }

  /// Adds a medication and schedules its daily reminder when enabled.
  Future<void> addEntry({
    required String name,
    required String dose,
    required TimeOfDay intakeTime,
    TimeOfDay? secondIntakeTime,
    required MedicationFrequency frequency,
    required bool remindersEnabled,
    MedicationCatalogItem? catalogItem,
  }) async {
    final entry = MedicationEntry(
      id: DateTime.now().millisecondsSinceEpoch.remainder(2147483647),
      name: name.trim(),
      dose: dose.trim(),
      intakeTime: intakeTime,
      secondIntakeTime: secondIntakeTime,
      frequency: frequency,
      remindersEnabled: remindersEnabled,
      createdAt: DateTime.now(),
      catalogItem: catalogItem,
    );

    _entries = _sortedEntries([..._entries, entry]);
    await _repository.saveEntries(_entries);
    await _notificationService.scheduleReminders(entry);
    _notifyIfActive();
  }

  /// Updates reminder state for a single medication entry.
  Future<void> toggleReminder(
    MedicationEntry entry,
    bool remindersEnabled,
  ) async {
    final updatedEntry = entry.copyWith(remindersEnabled: remindersEnabled);
    _entries = _entries
        .map(
          (currentEntry) =>
              currentEntry.id == entry.id ? updatedEntry : currentEntry,
        )
        .toList();

    await _repository.saveEntries(_entries);
    await _notificationService.scheduleReminders(
      updatedEntry,
      skippedDoseIndexes: _takenDoseIndexesForToday(updatedEntry),
    );
    _notifyIfActive();
  }

  /// Deletes a medication entry and removes its pending notification.
  Future<void> deleteEntry(MedicationEntry entry) async {
    _entries = _entries
        .where((currentEntry) => currentEntry.id != entry.id)
        .toList();

    await _repository.saveEntries(_entries);
    await _notificationService.cancelReminders(entry);
    _notifyIfActive();
  }

  /// Stores whether one medication was taken on a specific calendar day.
  Future<void> toggleTakenForDate(
    MedicationEntry entry,
    DateTime date,
    int doseIndex,
    bool isTaken,
  ) async {
    if (isTaken && _isFutureDate(date)) {
      return;
    }

    final dateKey = medicationDoseDateKey(date, doseIndex);
    final updatedDateKeys = entry.takenDateKeys.toSet();

    if (isTaken) {
      updatedDateKeys.add(dateKey);
    } else {
      updatedDateKeys.remove(dateKey);
    }

    final updatedEntry = entry.copyWith(
      takenDateKeys: updatedDateKeys.toList()..sort(),
    );

    _entries = _entries
        .map(
          (currentEntry) =>
              currentEntry.id == entry.id ? updatedEntry : currentEntry,
        )
        .toList();

    await _repository.saveEntries(_entries);
    if (_isToday(date)) {
      if (isTaken) {
        await _notificationService.cancelReminder(entry.id, doseIndex);
      } else if (updatedEntry.remindersEnabled) {
        await _notificationService.scheduleReminders(
          updatedEntry,
          skippedDoseIndexes: _takenDoseIndexesForToday(updatedEntry),
        );
      }
    }
    _notifyIfActive();
  }

  /// Reconciles today's notification state with medications already taken today.
  Future<void> _syncTodayReminders() async {
    for (final entry in _entries) {
      if (!entry.remindersEnabled) {
        continue;
      }

      await _notificationService.scheduleReminders(
        entry,
        skippedDoseIndexes: _takenDoseIndexesForToday(entry),
      );
    }
  }

  Set<int> _takenDoseIndexesForToday(MedicationEntry entry) {
    final today = DateTime.now();

    return {
      for (var index = 0; index < entry.intakeTimes.length; index++)
        if (entry.takenDateKeys.contains(medicationDoseDateKey(today, index)))
          index,
    };
  }

  /// Compares calendar days instead of exact DateTime values.
  bool _isToday(DateTime date) {
    final now = DateTime.now();
    return date.year == now.year &&
        date.month == now.month &&
        date.day == now.day;
  }

  /// Prevents users from marking medication as taken before the day arrives.
  bool _isFutureDate(DateTime date) {
    final now = DateTime.now();
    final selectedDay = DateTime(date.year, date.month, date.day);
    final currentDay = DateTime(now.year, now.month, now.day);

    return selectedDay.isAfter(currentDay);
  }

  /// Orders medication entries by intake time for predictable daily lists.
  List<MedicationEntry> _sortedEntries(List<MedicationEntry> entries) {
    return entries..sort((a, b) {
      final aMinutes = a.intakeTime.hour * 60 + a.intakeTime.minute;
      final bMinutes = b.intakeTime.hour * 60 + b.intakeTime.minute;
      return aMinutes.compareTo(bMinutes);
    });
  }

  void _notifyIfActive() {
    if (!_isDisposed) {
      notifyListeners();
    }
  }

  @override
  void dispose() {
    _isDisposed = true;
    super.dispose();
  }
}