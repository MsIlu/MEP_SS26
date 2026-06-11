import 'dart:convert';

import 'package:app1/core/network/api_client.dart';
import 'package:app1/core/network/api_exception.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

void main() {
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
}
