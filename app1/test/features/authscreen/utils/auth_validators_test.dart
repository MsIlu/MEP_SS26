import 'package:flutter_test/flutter_test.dart';

import 'package:app1/features/authscreen/utils/auth_validators.dart';

void main() {
  group('AuthValidators.newPassword', () {
    test('rejects passwords without all strength requirements', () {
      expect(AuthValidators.newPassword('12345678'), isNotNull);
      expect(AuthValidators.newPassword('Password'), isNotNull);
      expect(AuthValidators.newPassword('password1!'), isNotNull);
      expect(AuthValidators.newPassword('PASSWORD1!'), isNotNull);
      expect(AuthValidators.newPassword('Password!'), isNotNull);
      expect(AuthValidators.newPassword('Password1'), isNotNull);
    });

    test(
      'accepts passwords with length, cases, number and special character',
      () {
        expect(AuthValidators.newPassword('Password1!'), isNull);
      },
    );
  });
}
