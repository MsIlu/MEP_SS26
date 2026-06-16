import 'package:flutter_test/flutter_test.dart';

import 'package:app1/features/authscreen/domain/models/account.dart';
import 'package:app1/features/authscreen/domain/models/auth_response.dart';
import 'package:app1/features/authscreen/state/auth_session.dart';

void main() {
  // Test case references: documents/Testfaelle_Frontend.md#t04-auth-und-registrierung
  group('AuthSession', () {
    test('stores auth response and selects first profile as active profile', () {
      final session = AuthSession();

      final response = AuthResponse(
        accessToken: 'test-token',
        tokenType: 'bearer',
        account: const Account(
          id: 1,
          email: 'test@example.com',
        ),
        profiles: const [
          AuthProfile(
            id: 10,
            displayName: 'Anna',
            profileType: 'self',
            role: 'owner',
          ),
          AuthProfile(
            id: 11,
            displayName: 'Ben',
            profileType: 'child',
            role: 'guardian',
          ),
        ],
      );

      session.setAuthResponse(response);

      expect(session.accessToken, 'test-token');
      expect(session.account?.email, 'test@example.com');
      expect(session.profiles.length, 2);
      expect(session.activeProfileId, 10);
      expect(session.activeProfile?.displayName, 'Anna');
      expect(session.isAuthenticated, true);
      expect(session.hasActiveProfile, true);
    });

    test('changes active profile by id', () {
      final session = AuthSession();

      session.setAuthResponse(
        AuthResponse(
          accessToken: 'test-token',
          tokenType: 'bearer',
          account: const Account(
            id: 1,
            email: 'test@example.com',
          ),
          profiles: const [
            AuthProfile(
              id: 10,
              displayName: 'Anna',
              profileType: 'self',
              role: 'owner',
            ),
            AuthProfile(
              id: 11,
              displayName: 'Ben',
              profileType: 'child',
              role: 'guardian',
            ),
          ],
        ),
      );

      session.setActiveProfileById(11);

      expect(session.activeProfileId, 11);
      expect(session.activeProfile?.displayName, 'Ben');
    });

    test('throws when selected profile is not part of current session', () {
      final session = AuthSession();

      session.setAuthResponse(
        AuthResponse(
          accessToken: 'test-token',
          tokenType: 'bearer',
          account: const Account(
            id: 1,
            email: 'test@example.com',
          ),
          profiles: const [
            AuthProfile(
              id: 10,
              displayName: 'Anna',
              profileType: 'self',
              role: 'owner',
            ),
          ],
        ),
      );

      expect(
            () => session.setActiveProfileById(999),
        throwsA(isA<StateError>()),
      );
    });

    test('clears auth session data', () {
      final session = AuthSession();

      session.setAuthResponse(
        AuthResponse(
          accessToken: 'test-token',
          tokenType: 'bearer',
          account: const Account(
            id: 1,
            email: 'test@example.com',
          ),
          profiles: const [
            AuthProfile(
              id: 10,
              displayName: 'Anna',
              profileType: 'self',
              role: 'owner',
            ),
          ],
        ),
      );

      session.clear();

      expect(session.accessToken, null);
      expect(session.account, null);
      expect(session.profiles, isEmpty);
      expect(session.activeProfile, null);
      expect(session.activeProfileId, null);
      expect(session.isAuthenticated, false);
      expect(session.hasActiveProfile, false);
    });
  });
}
