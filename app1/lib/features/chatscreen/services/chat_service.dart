import '../data/models/chat_response_model.dart';
import '../data/models/message_model.dart';

/// Handles chat-domain message operations without depending on Flutter UI state.
class ChatService {
  static const Duration defaultTypingDelay = Duration(milliseconds: 15);

  List<Message> addMessage({
    required List<Message> messages,
    required Message message,
  }) {
    return List<Message>.from(messages)..add(message);
  }

  List<Message> removeLastBotMessage(List<Message> messages) {
    final updated = List<Message>.from(messages);

    for (int i = updated.length - 1; i >= 0; i--) {
      if (!updated[i].isUser) {
        updated.removeAt(i);
        break;
      }
    }

    return updated;
  }

  List<Message> replaceLastMessage({
    required List<Message> messages,
    required Message message,
  }) {
    if (messages.isEmpty) {
      return [message];
    }

    final updated = List<Message>.from(messages);
    updated[updated.length - 1] = message;
    return updated;
  }

  Message buildAssistantMessage(ChatResponse response) {
    final canCreateAppointment = hasAppointmentRecommendation(response);

    return Message(
      text: response.text,
      isUser: false,
      canExportPdf: hasRecommendation(response),
      exportTitle: 'Handlungsempfehlung',
      exportRecommendation: response.text,
      exportNextSteps: response.action,
      canCreateAppointment: canCreateAppointment,
      appointmentTitle: canCreateAppointment
          ? _appointmentTitleForRecommendation(response.text)
          : null,
    );
  }

  bool hasRecommendation(ChatResponse response) {
    final responseText = response.text.toLowerCase();

    return (response.action != null && response.action!.trim().isNotEmpty) ||
        responseText.contains('dringlichkeit:') ||
        responseText.contains('empfohlene versorgungsebene:') ||
        responseText.contains('nächster schritt:') ||
        responseText.contains('naechster schritt:') ||
        responseText.contains('hinweis:');
  }

  bool hasAppointmentRecommendation(ChatResponse response) {
    final responseText = response.text.toLowerCase();
    final actionText = response.action?.toLowerCase() ?? '';
    final combinedText = '$responseText $actionText';

    return combinedText.contains('hausarzt') ||
        combinedText.contains('facharzt') ||
        combinedText.contains('arztbesuch') ||
        combinedText.contains('arzttermin') ||
        combinedText.contains('ärztlich') ||
        combinedText.contains('aerztlich');
  }

  String _appointmentTitleForRecommendation(String text) {
    final lowerText = text.toLowerCase();

    if (lowerText.contains('hausarzt')) {
      return 'Hausarzttermin vereinbaren';
    }

    if (lowerText.contains('facharzt')) {
      return 'Facharzttermin vereinbaren';
    }

    return 'Arzttermin vereinbaren';
  }

  Stream<String> streamText(
    String fullText, {
    Duration delay = defaultTypingDelay,
  }) async* {
    var current = '';

    for (final codePoint in fullText.runes) {
      await Future.delayed(delay);
      current += String.fromCharCode(codePoint);
      yield current;
    }
  }
}
