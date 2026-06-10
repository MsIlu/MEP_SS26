import '../../../core/network/api_exception.dart';

class AuthErrorMessage {
  static String registration(Object error) {
    if (error is! ApiException) {
      return 'Registrierung fehlgeschlagen. Bitte versuche es erneut.';
    }

    if (error.type == ApiErrorType.timeout) {
      return 'Der Server antwortet zu langsam. Bitte versuche es erneut.';
    }

    if (error.type == ApiErrorType.network) {
      return 'Der Server ist nicht erreichbar. Bitte prüfe deine Verbindung.';
    }

    if (error.statusCode == 400 &&
        error.message == 'Email is already registered.') {
      return 'Diese E-Mail-Adresse wird bereits verwendet. Bitte melde dich an oder nutze eine andere Adresse.';
    }

    if (error.statusCode == 422) {
      return 'Ein Feld konnte nicht verarbeitet werden. Bitte überprüfe deine Angaben.';
    }

    return 'Registrierung fehlgeschlagen. Bitte versuche es erneut.';
  }
}