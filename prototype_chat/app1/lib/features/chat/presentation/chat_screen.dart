import 'package:app1/features/chat/presentation/themes/app_colors.dart';
import 'package:flutter/material.dart';
import 'chat_controller.dart';
import 'widgets/chat_bubble.dart';
import '../../../../core/config/app_config.dart';

/// Hauptscreen der Chat-Anwendung.
///
/// Verantwortlich für UI Darstellung und User Input Handling.
class ChatScreen extends StatefulWidget {
  final ChatController controller;

  const ChatScreen({
    super.key,
    required this.controller,
  });

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

/// Interner State des ChatScreen Widgets.
///
/// Diese Klasse verwaltet alle UI-spezifischen Ressourcen und Logik,
/// die nicht im Controller liegen sollten.
///
/// Verantwortlichkeiten:
/// - Verwaltung der Text-Eingabe (TextEditingController)
/// - Scroll-Position der Chat-Liste (ScrollController)
/// - Session-ID für den Chat-Verlauf
/// - Lebenszyklus-Management (initState / dispose)
/// - Triggern von Controller-Aktionen beim Start und beim Senden von Nachrichten

class _ChatScreenState extends State<ChatScreen> {
  final textController = TextEditingController();
  final scrollController = ScrollController();

  final sessionId = UniqueKey().toString();

  /// Wird einmal beim Erstellen des Widgets aufgerufen.
  ///
  /// Initialisiert den Chat:
  /// - führt einen Warmup-Call zum Backend aus
  /// - fügt eine Begrüßungsnachricht hinzu
  @override
  void initState() {
    super.initState();
    widget.controller.warmup();
    widget.controller.addWelcomeMessage();
  }

  /// Wird beim Entfernen des Widgets aufgerufen.
  ///
  /// Gibt alle Ressourcen frei:
  /// - TextController (verhindert Memory Leaks)
  /// - ScrollController
  @override
  void dispose() {
    textController.dispose();
    scrollController.dispose();
    super.dispose();
  }

  /// Sendet eine Nachricht an den ChatController.
  ///
  /// Ablauf:
  /// - liest Text aus dem Eingabefeld
  /// - übergibt ihn an den Controller
  /// - setzt Eingabefeld zurück

  Future<void> send() async {
    final text = textController.text.trim();
    if (text.isEmpty) return;

    textController.clear();

    widget.controller.sendMessage(text, sessionId);

    // Auto-Scroll nach neuer Nachricht
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (scrollController.hasClients) {
        scrollController.jumpTo(
          scrollController.position.maxScrollExtent,
        );
      }
    });
  }

  /// Baut die Benutzeroberfläche des ChatScreens.
  ///
  /// Diese Methode beschreibt die komplette UI-Struktur der Chat-Anwendung:
  ///
  /// Aufbau:
  /// - AppBar mit App-Titel
  /// - Chatbereich (Liste der Nachrichten)
  /// - Eingabebereich (Textfeld + Send-Button)
  ///
  /// Die Chatnachrichten werden über einen ValueListenableBuilder
  /// reaktiv aus dem ChatController gelesen und automatisch neu gerendert,
  /// sobald sich die Nachrichtenliste ändert.
  ///
  /// Die Nachrichten werden als Liste von ChatBubble Widgets dargestellt.
  ///
    @override
  Widget build(BuildContext context) {
    return Scaffold(
      //  Namensleiste (obere Bar)
      appBar: AppBar(
        title: const Text(AppConfig.appName),
        backgroundColor: AppColors.upperBarColor,
      ),
      body: Column(
        children: [
          /// Chatverlauf Bereich
          Expanded(
            child: ValueListenableBuilder(
              valueListenable: widget.controller.messages,
              builder: (context, messages, _) {
                return ListView.builder(
                  controller: scrollController,
                  itemCount: messages.length,
                  itemBuilder: (_, i) {
                    return ChatBubble(
                      message: messages[i],
                    );
                  },
                );
              },
            ),
          ),

          ///  Input Bereich (untere Bar)
          Container(
            color: AppColors.lowerBarColor,
            padding: const EdgeInsets.symmetric(
              horizontal: 8,
              vertical: 6,
            ),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: textController,
                    onSubmitted: (_) => send(),
                    decoration: const InputDecoration(
                      hintText: "Nachricht eingeben...",
                      border: InputBorder.none,
                    ),
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.send),
                  onPressed: send,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}