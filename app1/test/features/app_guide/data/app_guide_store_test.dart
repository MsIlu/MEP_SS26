import 'package:app1/features/app_guide/data/app_guide_store.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  test('stores guide completion separately for accounts and guests', () async {
    SharedPreferences.setMockInitialValues({});
    final store = AppGuideStore();
    final firstAccount = AppGuideStore.accountKey(1);
    final secondAccount = AppGuideStore.accountKey(2);

    expect(AppGuideStore.accountKey(0), isNot(AppGuideStore.guestKey));
    expect(await store.isCompleted(firstAccount), isFalse);
    expect(await store.isCompleted(secondAccount), isFalse);
    expect(await store.isCompleted(AppGuideStore.guestKey), isFalse);

    await store.markCompleted(firstAccount);
    await store.markCompleted(AppGuideStore.guestKey);

    expect(await store.isCompleted(firstAccount), isTrue);
    expect(await store.isCompleted(secondAccount), isFalse);
    expect(await store.isCompleted(AppGuideStore.guestKey), isTrue);
  });
}
