/*
Hinweise: 
Standardmäßig sollte Web und Android Emulator funktionieren.
Wenn ihr direkt auf eurem Handy testen wollt, dann im Terminal

flutter run --dart-define=serverURL=http://141.19.146.196:8000

wichtige Befehle
flutter run ( -d <device name>)
flutter clean
flutter devices
flutter emulators
flutter emulators --launch <device name>

Um Android Emulator zu nutzen müsst ihr Android Studio installieren:
https://developer.android.com/studio?hl=de#get-android-studio

Flutter installieren:
https://docs.flutter.dev/install/quick
*/

import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:uuid/uuid.dart';

// Anzeigename der Anwendung
final String appName = "MedBitAid - Proto v0.2";

// Verwendung mit Android Emulator & Web
final String serverURL = kIsWeb
    ? "http://localhost:8000"     // Web (Browser)
    : "http://10.0.2.2:8000";    // Android Emulator
// Verwendung mit externem Gerät (benötigt IP Adresse des Geräts das den Server hostet)
// Von dem Gerät auf dem der Server läuft Hotspot fürs handy, danach sollte es gehen
// zum testen: im browser <eureIP>/docs
// wenn API Dokumentation kommt müssts funktionieren, ansonsten sieht euer Handy den Server nicht.
// final String serverURL = "141.19.146.196:8000";

void main() {
  runApp(ChatApp());
}

class ChatApp extends StatelessWidget {
  const ChatApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: ChatScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  _ChatScreenState createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final controller = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  // Session ID
  final String sessionId = const Uuid().v4();

  // Message Struktur
  List<Map<String, dynamic>> messages = [];

  @override
  void initState() {
    super.initState();

    messages.add({
      "text": "Hallo! 👋 Wie kann ich dir helfen?",
      "isUser": false
      });

    preloadModel();
    }

  // Vorab Laden des Modells
  Future<void> preloadModel() async {
    try {
      await http.post(
        Uri.parse(serverURL).resolve("/warmup"),
      );
    } catch (e) {
      print("❌ Warmup Fehler: $e");
    }
  }

  // -------------------------
  // Nachricht senden
  // -------------------------
  Future<void> sendMessage(String text) async {
    if (text.trim().isEmpty) return;

    setState(() {
      messages.add({"text": text, "isUser": true});
    });

    scrollToBottom();

    try {
      final response = await http.post(
        Uri.parse(serverURL).resolve("/chat"),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "message": text,
          "session_id": sessionId,
        }),
      );

      final data = jsonDecode(response.body);

      setState(() {
        messages.add({"text": data["response"], "isUser": false});
      });

      scrollToBottom();
    } catch (e) {
      setState(() {
        messages.add({"text": "❌ Fehler: $e", "isUser": false});
      });
    }
  }

  // -------------------------
  // Auto Scroll
  // -------------------------
  void scrollToBottom() {
    Future.delayed(Duration(milliseconds: 100), () {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  // -------------------------
  // Chat Bubble
  // -------------------------
  Widget buildMessage(String text, bool isUser) {
    return Align(
      alignment:
          isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: EdgeInsets.symmetric(vertical: 4, horizontal: 8),
        padding: EdgeInsets.all(12),
        constraints: BoxConstraints(maxWidth: 300),
        decoration: BoxDecoration(
          color: isUser ? Colors.blue[400] : Colors.grey[300],
          borderRadius: BorderRadius.circular(12),
        ),
        child: Text(
          text,
          style: TextStyle(
            color: isUser ? Colors.white : Colors.black,
          ),
        ),
      ),
    );
  }

  // -------------------------
  // UI
  // -------------------------
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(appName),
        backgroundColor: Colors.blue[800],
      ),
      body: Column(
        children: [
          // Chat Liste
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              itemCount: messages.length,
              itemBuilder: (context, index) {
                final msg = messages[index];
                return buildMessage(msg["text"], msg["isUser"]);
              },
            ),
          ),

          Divider(height: 1),

          // Input Feld
          Container(
            padding: EdgeInsets.symmetric(horizontal: 8, vertical: 6),
            color: Colors.grey[300],
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: controller,
                    decoration: InputDecoration(
                      hintText: "Nachricht eingeben...",
                      border: InputBorder.none,
                    ),
                    onSubmitted: (value) {
                      sendMessage(value);
                      controller.clear();
                    },
                  ),
                ),
                IconButton(
                  icon: Icon(Icons.send, color: Colors.blue),
                  onPressed: () {
                    sendMessage(controller.text);
                    controller.clear();
                  },
                )
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// Helfer Klasse für richtige URL entsprechend der Plattform
class Config {
  static String get baseUrl {
    if (kIsWeb) return "http://localhost:8000";
    if (Platform.isAndroid) return "http://10.0.2.2:8000";
    return "http://192.168.178.69:8000";
  }
}