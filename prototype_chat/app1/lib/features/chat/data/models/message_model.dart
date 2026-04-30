/// Datenmodell für eine Chat-Nachricht.
///
/// Enthält Text und Information, ob die Nachricht vom User stammt.
class Message {
  final String text;
  final bool isUser;

  const Message({
    required this.text,
    required this.isUser,
  });
}