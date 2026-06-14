import 'package:app1/features/app_guide/data/app_guide_store.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  test('stores guide completion per account', () async {
    SharedPreferences.setMockInitialValues({});
    final store = AppGuideStore();

    expect(await store.isCompleted(1), isFalse);
    expect(await store.isCompleted(2), isFalse);

    await store.markCompleted(1);

    expect(await store.isCompleted(1), isTrue);
    expect(await store.isCompleted(2), isFalse);
  });
}