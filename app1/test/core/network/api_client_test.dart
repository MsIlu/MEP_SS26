import 'dart:async';
import 'dart:convert';

import 'package:app1/core/network/api_client.dart';
import 'package:app1/core/network/api_exception.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

void main() {
  group('Email registration error', () {
    test('extracts the backend detail from HTTP errors', () async {
      final client = ApiClient(
        MockClient(
          (_) async => http.Response(
            jsonEncode({'detail': 'Email is already registered.'}),
            400,
            headers: {'content-type': 'application/json'},
          ),
        ),
      );

      await expectLater(
        client.post('/auth/register', const {}),
        throwsA(
          isA<ApiException>()
              .having((error) => error.statusCode, 'statusCode', 400)
              .having(
                (error) => error.message,
                'message',
                'Email is already registered.',
              ),
        ),
      );
    });
  });

  group('ApiClient HTTP errors', () {
    const expectedMessages = {
      400: 'Die Anfrage ist ungültig. Bitte überprüfen Sie Ihre Eingaben.',
      401: 'Sie sind nicht angemeldet. Bitte melden Sie sich erneut an.',
      403: 'Sie haben keine Berechtigung für diese Aktion.',
      404: 'Die angefragten Daten wurden nicht gefunden.',
      500:
          'Es ist ein Serverfehler aufgetreten. Bitte versuchen Sie es später erneut.',
    };

    for (final entry in expectedMessages.entries) {
      test('get maps ${entry.key} to a user-facing message', () async {
        final client = ApiClient(
          MockClient(
            (_) async => http.Response(
              jsonEncode({'detail': 'Backend detail should not leak.'}),
              entry.key,
              headers: {'content-type': 'application/json'},
            ),
          ),
        );

        await expectLater(
          client.get('/profiles/1'),
          throwsA(
            isA<ApiException>()
                .having((error) => error.type, 'type', ApiErrorType.http)
                .having((error) => error.statusCode, 'statusCode', entry.key)
                .having((error) => error.message, 'message', entry.value),
          ),
        );
      });

      test('getList maps ${entry.key} to a user-facing message', () async {
        final client = ApiClient(
          MockClient(
            (_) async => http.Response(
              jsonEncode({'detail': 'Backend detail should not leak.'}),
              entry.key,
              headers: {'content-type': 'application/json'},
            ),
          ),
        );

        await expectLater(
          client.getList('/profiles'),
          throwsA(
            isA<ApiException>()
                .having((error) => error.type, 'type', ApiErrorType.http)
                .having((error) => error.statusCode, 'statusCode', entry.key)
                .having((error) => error.message, 'message', entry.value),
          ),
        );
      });
    }
  });

  group('ApiClient invalid responses', () {
    test('get throws invalidResponse when JSON is not an object', () async {
      final client = ApiClient(
        MockClient(
          (_) async => http.Response(
            jsonEncode(['not', 'an', 'object']),
            200,
            headers: {'content-type': 'application/json'},
          ),
        ),
      );

      await expectLater(
        client.get('/auth/me'),
        throwsA(
          isA<ApiException>()
              .having(
                (error) => error.type,
                'type',
                ApiErrorType.invalidResponse,
              )
              .having(
                (error) => error.message,
                'message',
                contains('Serverantwort konnte nicht verarbeitet werden'),
              ),
        ),
      );
    });

    test('getList throws invalidResponse when JSON is not a list', () async {
      final client = ApiClient(
        MockClient(
          (_) async => http.Response(
            jsonEncode({'not': 'a list'}),
            200,
            headers: {'content-type': 'application/json'},
          ),
        ),
      );

      await expectLater(
        client.getList('/profiles'),
        throwsA(
          isA<ApiException>()
              .having(
                (error) => error.type,
                'type',
                ApiErrorType.invalidResponse,
              )
              .having(
                (error) => error.message,
                'message',
                contains('Serverantwort konnte nicht verarbeitet werden'),
              ),
        ),
      );
    });
  });

  group('ApiClient timeouts', () {
    test('get converts TimeoutException into timeout ApiException', () async {
      final client = ApiClient(
        MockClient((_) async => throw TimeoutException('Request timed out')),
      );

      await expectLater(
        client.get('/auth/me'),
        throwsA(
          isA<ApiException>()
              .having((error) => error.type, 'type', ApiErrorType.timeout)
              .having(
                (error) => error.message,
                'message',
                contains('Server hat nicht rechtzeitig geantwortet'),
              ),
        ),
      );
    });

    test(
      'getList converts TimeoutException into timeout ApiException',
      () async {
        final client = ApiClient(
          MockClient((_) async => throw TimeoutException('Request timed out')),
        );

        await expectLater(
          client.getList('/profiles'),
          throwsA(
            isA<ApiException>()
                .having((error) => error.type, 'type', ApiErrorType.timeout)
                .having(
                  (error) => error.message,
                  'message',
                  contains('Server hat nicht rechtzeitig geantwortet'),
                ),
          ),
        );
      },
    );
  });
}
