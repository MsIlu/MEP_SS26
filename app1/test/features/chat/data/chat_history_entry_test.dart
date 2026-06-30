import 'package:app1/features/chatscreen/data/models/chat_history_entry.dart';
import 'package:app1/features/chatscreen/data/models/message_model.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  // Test case references: documents/Testfaelle_Frontend.md#t02-chat-history
  group('ChatHistoryEntry', () {
    test('parses UTC timestamps into local user time', () {
      final entry = ChatHistoryEntry.fromJson({
        'id': 1,
        'profile_id': 42,
        'title': 'Atemnot',
        'status': 'completed',
        'is_emergency': true,
        'created_at': '2026-06-14T16:55:00+00:00',
        'updated_at': '2026-06-14T17:05:00+00:00',
        'recommendation': 'Notruf 112',
        'messages': const [],
      });

      expect(entry.createdAt.isUtc, isFalse);
      expect(entry.createdAt, DateTime.utc(2026, 6, 14, 16, 55).toLocal());

      expect(entry.status, 'completed');
      expect(entry.updatedAt, DateTime.utc(2026, 6, 14, 17, 5).toLocal());
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

    test('uses a one-word title and falls back to Verlauf', () {
      final titledEntry = _entry(
        symptomTitle: 'Starke Kopfschmerzen seit heute',
      );
      final blankEntry = _entry(symptomTitle: '   ');

      expect(titledEntry.title, 'Starke');
      expect(blankEntry.title, 'Verlauf');
    });

    test('prefers the first user message as preview', () {
      final entry = _entry(
        recommendation: 'Hausarztpraxis regulaer',
        messages: [
          Message(text: '', isUser: true),
          Message(text: 'Bitte warten', isUser: false),
          Message(text: 'Ich habe Bauchschmerzen', isUser: true),
        ],
      );

      expect(entry.preview, 'Ich habe Bauchschmerzen');
    });

    test('round-trips messages and export fields through encoded JSON', () {
      final entry = _entry(
        messages: [
          Message(
            text: 'Empfehlung',
            isUser: false,
            timestamp: DateTime.utc(2026, 6, 14, 16, 55),
            canExportPdf: true,
            exportTitle: 'Kopfschmerzen',
            exportRecommendation: 'Hausarztpraxis regulaer',
            exportNextSteps: 'Termin vereinbaren',
            canCreateAppointment: true,
            appointmentTitle: 'Hausarzttermin vereinbaren',
            recommendationSymptoms: const ['Kopfschmerzen', 'Uebelkeit'],
            documentSaved: true,
            symptomsSaved: true,
            appointmentSearched: true,
          ),
        ],
      );

      final decoded = ChatHistoryEntry.decode(entry.encode());

      expect(decoded.messages, hasLength(1));
      expect(decoded.messages.single.canExportPdf, isTrue);
      expect(decoded.messages.single.exportTitle, 'Kopfschmerzen');
      expect(decoded.messages.single.exportNextSteps, 'Termin vereinbaren');
      expect(decoded.messages.single.canCreateAppointment, isTrue);
      expect(
        decoded.messages.single.appointmentTitle,
        'Hausarzttermin vereinbaren',
      );
      expect(decoded.messages.single.recommendationSymptoms, [
        'Kopfschmerzen',
        'Uebelkeit',
      ]);
      expect(decoded.messages.single.documentSaved, isTrue);
      expect(decoded.messages.single.symptomsSaved, isTrue);
      expect(decoded.messages.single.appointmentSearched, isTrue);
    });
  });
}

ChatHistoryEntry _entry({
  String? symptomTitle = 'Kopfschmerzen',
  String recommendation = 'Selbstbeobachtung',
  List<Message> messages = const [],
}) {
  return ChatHistoryEntry(
    id: '1',
    profileId: 42,
    symptomTitle: symptomTitle,
    isEmergency: false,
    createdAt: DateTime(2026, 6, 14, 18, 55),
    messages: messages,
    recommendation: recommendation,
  );
}
