import 'package:flutter_test/flutter_test.dart';
import 'package:app1/features/chatscreen/utils/smart_replies.dart';

/// Unit tests for deterministic smart reply keyword paths.
void main() {
  group('SmartReplies', () {
    test('generates pain follow-ups for pain-related input', () {
      final result = SmartReplies.generate('Ich habe starke Bauchschmerzen');

      expect(result, contains('Wo genau tut es weh?'));
      expect(result, contains('Seit wann habe ich das?'));
      expect(result, hasLength(3));
    });

    test('falls back to general follow-ups for neutral input', () {
      final result = SmartReplies.generate('Hallo Careena');

      expect(result, contains('Erklär mir das einfacher'));
      expect(result, contains('Was soll ich jetzt tun?'));
    });
  });
}
