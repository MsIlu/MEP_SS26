import 'package:flutter_test/flutter_test.dart';

import 'package:app1/features/authscreen/domain/models/auth_response.dart';

void main() {
  group('AuthResponse', () {
    test('fromJson parses account, token and profiles', () {
      final response = AuthResponse.fromJson({
        'access_token': 'test-token',
        'token_type': 'bearer',
        'account': {
          'id': 1,
          'email': 'test@example.com',
        },
        'profiles': [
          {
            'id': 10,
            'display_name': 'Anna',
            'profile_type': 'self',
            'role': 'owner',
          },
          {
            'id': 11,
            'display_name': 'Ben',
            'profile_type': 'child',
            'role': 'guardian',
          },
        ],
      });

      expect(response.accessToken, 'test-token');
      expect(response.tokenType, 'bearer');

      expect(response.account.id, 1);
      expect(response.account.email, 'test@example.com');

      expect(response.profiles.length, 2);

      expect(response.profiles.first.id, 10);
      expect(response.profiles.first.displayName, 'Anna');
      expect(response.profiles.first.profileType, 'self');
      expect(response.profiles.first.role, 'owner');

      expect(response.profiles[1].id, 11);
      expect(response.profiles[1].displayName, 'Ben');
      expect(response.profiles[1].profileType, 'child');
      expect(response.profiles[1].role, 'guardian');
    });
  });
}