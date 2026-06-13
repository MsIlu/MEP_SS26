import '../../../core/network/api_client.dart';
import '../domain/symptom_response.dart';

class SymptomApiService {
  /// API client used to communicate with the backend.
  final ApiClient _apiClient;

  const SymptomApiService(this._apiClient);

  /// Loads all symptom diary entries for a profile.
  Future<List<SymptomResponse>> getSymptoms({
    required int profileId,
  }) async {
    final response = await _apiClient.getList('/profiles/$profileId/symptoms');

    return response
        .map((item) => SymptomResponse.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  /// Creates one symptom diary entry for a profile.
  Future<SymptomResponse> createSymptom({
    required int profileId,
    required DateTime date,
    required String symptom,
    String bodyArea = '',
    required int intensity,
    required String note,
    DateTime? createdAt,
  }) async {
    final response = await _apiClient.post(
      '/profiles/$profileId/symptoms',
      {
        'date': date.toIso8601String(),
        'symptom': symptom,
        'bodyArea': bodyArea,
        'intensity': intensity,
        'note': note,
        'createdAt': (createdAt ?? DateTime.now()).toIso8601String(),
      },
    );

    return SymptomResponse.fromJson(response);
  }
}
