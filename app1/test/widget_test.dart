import 'package:flutter_test/flutter_test.dart';

import 'package:app1/main.dart';

void main() {
  testWidgets('Home screen smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const MyApp());

    expect(find.text('Willkommen!'), findsOneWidget);
    expect(find.text('Jetzt mit Careena sprechen'), findsOneWidget);
  });
}
