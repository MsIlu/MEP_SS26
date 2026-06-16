import 'package:app1/core/network/api_exception.dart';
import 'package:app1/features/authscreen/utils/auth_error_message.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  // Test case references: documents/Testfaelle_Frontend_Aufgaben.md#t04-auth-und-registrierung
  test('explains duplicate email registration errors', () {
    const error = ApiException(
      ApiErrorType.http,
      'Email is already registered.',
      statusCode: 400,
    );

    expect(
      AuthErrorMessage.registration(error),
      contains('E-Mail-Adresse wird bereits verwendet'),
    );
  });

  test('explains unreachable server registration errors', () {
    const error = ApiException(ApiErrorType.network, 'Network Error');

    expect(
      AuthErrorMessage.registration(error),
      contains('Server ist nicht erreichbar'),
    );
  });
}
