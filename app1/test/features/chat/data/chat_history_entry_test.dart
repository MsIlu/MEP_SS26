import 'package:app1/features/chatscreen/data/models/chat_history_entry.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('ChatHistoryEntry', () {
    test('parses UTC timestamps into local user time', () {
      final entry = ChatHistoryEntry.fromJson({
        'id': 1,
        'profile_id': 42,
        'title': 'Atemnot',
        'is_emergency': true,
        'created_at': '2026-06-14T16:55:00+00:00',
        'recommendation': 'Notruf 112',
        'messages': const [],
      });

      expect(entry.createdAt.isUtc, isFalse);
      expect(entry.createdAt, DateTime.utc(2026, 6, 14, 16, 55).toLocal());
    });

    test('treats timezone-less backend timestamps as UTC', () {
      final entry = ChatHistoryEntry.fromJson({
        'id': 1,
        'profile_id': 42,
        'title': 'Atemnot',
        'is_emergency': true,
        'created_at': '2026-06-14T16:55:00',
        'recommendation': 'Notruf 112',
        'messages': const [],
      });

      expect(entry.createdAt.isUtc, isFalse);
      expect(entry.createdAt, DateTime.utc(2026, 6, 14, 16, 55).toLocal());
    });
  });
}
