import 'package:flutter/material.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:flutter_timezone/flutter_timezone.dart';
import 'package:timezone/data/latest_all.dart' as tz_data;
import 'package:timezone/timezone.dart' as tz;

import '../data/medication_entry.dart';
import '../data/medication_schedule.dart';

/// Wraps local notification setup and medication reminder scheduling.
class MedicationNotificationService {
  MedicationNotificationService._();

  static final MedicationNotificationService instance =
      MedicationNotificationService._();

  final FlutterLocalNotificationsPlugin _notifications =
      FlutterLocalNotificationsPlugin();

  bool _initialized = false;

  Future<void> initialize() async {
    if (_initialized) {
      return;
    }

    tz_data.initializeTimeZones();
    await _setLocalTimeZone();

    const androidSettings = AndroidInitializationSettings(
      '@mipmap/ic_launcher',
    );
    const darwinSettings = DarwinInitializationSettings();
    const linuxSettings = LinuxInitializationSettings(
      defaultActionName: 'Öffnen',
    );
    const initializationSettings = InitializationSettings(
      android: androidSettings,
      iOS: darwinSettings,
      macOS: darwinSettings,
      linux: linuxSettings,
    );

    await _notifications.initialize(settings: initializationSettings);
    await _requestPermissions();
    _initialized = true;
  }

  /// Schedules all active reminders for the entry's current intake pattern.
  Future<void> scheduleReminders(
    MedicationEntry entry, {
    Set<int> skippedDoseIndexes = const {},
  }) async {
    await initialize();
    await cancelReminders(entry);

    if (!entry.remindersEnabled) {
      return;
    }

    try {
      final times = entry.intakeTimes;
      for (var index = 0; index < times.length; index++) {
        if (skippedDoseIndexes.contains(index)) {
          continue;
        }

        for (final occurrence in _notificationOccurrences(entry)) {
          await _notifications.zonedSchedule(
            id: _notificationId(entry.id, index, occurrence.id),
            title: 'Medikament einnehmen',
            body: '${entry.name} - ${entry.dose}',
            scheduledDate: _nextOccurrence(
              times[index],
              weekday: occurrence.targetWeekday,
              dayOfMonth: occurrence.targetDayOfMonth,
            ),
            notificationDetails: const NotificationDetails(
              android: AndroidNotificationDetails(
                'medication_daily_reminders',
                'Medikamenten-Erinnerungen',
                channelDescription: 'Erinnerungen zur Medikamenteneinnahme',
                importance: Importance.high,
                priority: Priority.high,
              ),
              iOS: DarwinNotificationDetails(),
              macOS: DarwinNotificationDetails(),
            ),
            androidScheduleMode: AndroidScheduleMode.inexactAllowWhileIdle,
            matchDateTimeComponents: occurrence.matchDateTimeComponents,
          );
        }
      }
    } on UnimplementedError {
      return;
    }
  }

  Future<void> cancelReminder(int id, int doseIndex) async {
    await initialize();
    for (var occurrenceId = 0; occurrenceId <= 31; occurrenceId++) {
      await _notifications.cancel(
        id: _notificationId(id, doseIndex, occurrenceId),
      );
    }
  }

  Future<void> cancelReminders(MedicationEntry entry) async {
    await initialize();
    for (var index = 0; index < entry.intakeTimes.length; index++) {
      await cancelReminder(entry.id, index);
    }
  }

  Future<void> _requestPermissions() async {
    await _notifications
        .resolvePlatformSpecificImplementation<
          AndroidFlutterLocalNotificationsPlugin
        >()
        ?.requestNotificationsPermission();

    await _notifications
        .resolvePlatformSpecificImplementation<
          IOSFlutterLocalNotificationsPlugin
        >()
        ?.requestPermissions(alert: true, badge: true, sound: true);

    await _notifications
        .resolvePlatformSpecificImplementation<
          MacOSFlutterLocalNotificationsPlugin
        >()
        ?.requestPermissions(alert: true, badge: true, sound: true);
  }

  Future<void> _setLocalTimeZone() async {
    try {
      final currentTimeZone = await FlutterTimezone.getLocalTimezone();
      tz.setLocalLocation(tz.getLocation(currentTimeZone));
    } catch (_) {
      tz.setLocalLocation(tz.UTC);
    }
  }

  /// Finds the next matching date for daily, weekly, weekday, or monthly rules.
  tz.TZDateTime _nextOccurrence(
    TimeOfDay time, {
    int? weekday,
    int? dayOfMonth,
  }) {
    final now = tz.TZDateTime.now(tz.local);
    var scheduled = tz.TZDateTime(
      tz.local,
      now.year,
      now.month,
      now.day,
      time.hour,
      time.minute,
    );

    while (weekday != null && scheduled.weekday != weekday) {
      scheduled = scheduled.add(const Duration(days: 1));
    }

    while (dayOfMonth != null && scheduled.day != dayOfMonth) {
      scheduled = scheduled.add(const Duration(days: 1));
    }

    if (!scheduled.isAfter(now)) {
      scheduled = scheduled.add(const Duration(days: 1));
    }

    while (weekday != null && scheduled.weekday != weekday) {
      scheduled = scheduled.add(const Duration(days: 1));
    }

    while (dayOfMonth != null && scheduled.day != dayOfMonth) {
      scheduled = scheduled.add(const Duration(days: 1));
    }

    return scheduled;
  }

  /// Maps one medication schedule to platform recurrence components.
  List<_MedicationNotificationOccurrence> _notificationOccurrences(
    MedicationEntry entry,
  ) {
    return switch (entry.frequency) {
      MedicationFrequency.weekdays => [
        for (
          var weekday = DateTime.monday;
          weekday <= DateTime.friday;
          weekday++
        )
          _MedicationNotificationOccurrence.weekly(weekday),
      ],
      MedicationFrequency.weekly => [
        _MedicationNotificationOccurrence.weekly(entry.createdAt.weekday),
      ],
      MedicationFrequency.monthly => [
        _MedicationNotificationOccurrence.monthly(entry.createdAt.day),
      ],
      _ => const [_MedicationNotificationOccurrence.daily()],
    };
  }

  int _notificationId(int entryId, int doseIndex, int occurrenceId) {
    return (entryId + doseIndex * 1000003 + occurrenceId * 10007) & 0x7fffffff;
  }
}

class _MedicationNotificationOccurrence {
  final int id;
  final int? targetWeekday;
  final int? targetDayOfMonth;
  final DateTimeComponents matchDateTimeComponents;

  const _MedicationNotificationOccurrence.daily()
    : id = 0,
      targetWeekday = null,
      targetDayOfMonth = null,
      matchDateTimeComponents = DateTimeComponents.time;

  const _MedicationNotificationOccurrence.weekly(int weekday)
    : id = weekday,
      targetWeekday = weekday,
      targetDayOfMonth = null,
      matchDateTimeComponents = DateTimeComponents.dayOfWeekAndTime;

  const _MedicationNotificationOccurrence.monthly(int dayOfMonth)
    : id = dayOfMonth,
      targetWeekday = null,
      targetDayOfMonth = dayOfMonth,
      matchDateTimeComponents = DateTimeComponents.dayOfMonthAndTime;
}