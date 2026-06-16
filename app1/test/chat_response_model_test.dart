import 'package:flutter_test/flutter_test.dart';
import 'package:app1/features/chatscreen/data/models/chat_response_model.dart';

void main() {
  // Test case references: documents/Testfaelle_Frontend.md#t06-chat-core-und-ui
  group('ChatResponse', () {
    test('maps normal backend responses', () {
      final response = ChatResponse.fromJson({
        'response': 'Bitte trinken Sie Wasser.',
        'red_flag': false,
      });

      expect(response.text, 'Bitte trinken Sie Wasser.');
      expect(response.redFlag, isFalse);
      expect(response.matchedKeywords, isEmpty);
    });

    test('maps red flag metadata', () {
      final response = ChatResponse.fromJson({
        'response': 'Warnhinweis',
        'red_flag': true,
        'rule_name': 'Starke Blutung',
        'matched_keywords': ['blutung'],
      });

      expect(response.redFlag, isTrue);
      expect(response.ruleName, 'Starke Blutung');
      expect(response.matchedKeywords, ['blutung']);
    });

    test('uses readable fallback for invalid response payloads', () {
      final response = ChatResponse.fromJson({'red_flag': false});

      expect(response.text, 'Ungültige Serverantwort');
    });
  });
}
