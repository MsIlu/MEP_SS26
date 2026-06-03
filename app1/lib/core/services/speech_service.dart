import 'package:speech_to_text/speech_to_text.dart';
import 'package:flutter/foundation.dart';

/// Status der Spracherkennung
enum SpeechStatus { idle, listening, error }

class SpeechService {
  final SpeechToText _speech = SpeechToText();
  bool _isInitialized = false;

  SpeechStatus _status = SpeechStatus.idle;
  SpeechStatus get status => _status;

  VoidCallback? onListeningStopped;

  Future<bool> initialize() async {
    if (_isInitialized) return true;
    _isInitialized = await _speech.initialize(
      onError: (error) {
        _status = SpeechStatus.error;
      },
      onStatus: (status) {
        print("Speech Status: $status");
        if (status == 'done' || status == 'notListening') {
          _status = SpeechStatus.idle;
          onListeningStopped?.call();
        }
      },
    );

    return _isInitialized;
  }

  /// Gibt zurück ob gerade zugehört wird
  bool get isListening => _speech.isListening;

  /// Startet die Spracherkennung – onResult liefert den erkannten Text
  Future<void> listen({
    required Function(String text) onResult,
    String localeId = 'de-DE',
  }) async {
    if (!_isInitialized) {
      final success = await initialize();
      if (!success) {
        _status = SpeechStatus.error;
        return;
      }
    }

    _status = SpeechStatus.listening;

    await _speech.listen(
      localeId: localeId,
      partialResults: true,
      listenFor: const Duration(seconds: 30),
      pauseFor: const Duration(seconds: 10),
      cancelOnError: true,
      onResult: (result) {
        onResult(result.recognizedWords);
      },
    );
  }

  /// Mikrofon sauber stoppen
  Future<void> stop() async {
    await _speech.stop();
    _status = SpeechStatus.idle;
  }
}
