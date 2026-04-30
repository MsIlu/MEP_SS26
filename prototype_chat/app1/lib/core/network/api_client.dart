import 'package:http/http.dart' as http;
import '../config/app_config.dart';
import 'dart:convert';

///
/// HTTP-Client Wrapper für API Requests.
///
/// Kapselt die HTTP-Logik und sorgt dafür,
/// dass alle Requests zentral über diese Klasse laufen.
/// 
/// DEV NOTE:
/// Todo: HTTP Error Handling
class ApiClient {
  final http.Client _client;

  ApiClient(this._client);

  Future<http.Response> post(
    String path,
    Map<String, dynamic> body,
  ) {
    return _client.post(
      Uri.parse("${AppConfig.baseUrl}$path"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode(body),
    );
  }
}