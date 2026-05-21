import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:app1/features/chat/data/models/chat_response_model.dart';
import 'package:app1/features/chat/presentation/screens/chat_screen.dart';
import 'package:app1/features/homescreen/presentation/screens/home_screen.dart';
import 'package:app1/features/warning/presentation/screens/warning_page.dart';
import 'package:app1/main.dart';

void main() {
  testWidgets('Login opens the home screen', (WidgetTester tester) async {
    await tester.pumpWidget(const MyApp());

    expect(find.text('Anmelden'), findsOneWidget);

    await tester.tap(find.text('Anmelden'));
    await tester.pumpAndSettle();

    expect(find.byType(HomeScreen), findsOneWidget);
    expect(find.text('Willkommen!'), findsOneWidget);
  });

  testWidgets('Primary onboarding action opens the chat', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const MyApp());

    await tester.tap(find.text('Jetzt mit Careena sprechen'));
    await tester.pump();

    expect(find.byType(ChatScreen), findsOneWidget);
  });

  testWidgets('Warning page shows emergency action', (
    WidgetTester tester,
  ) async {
    const response = ChatResponse(
      text: 'Warnhinweis',
      redFlag: true,
      ruleName: 'Starke oder unstillbare Blutung',
      category: 'bleeding',
      matchedKeywords: ['starke blutung'],
    );

    await tester.pumpWidget(
      const MaterialApp(home: WarningPage(response: response)),
    );

    expect(find.text('Handlungsempfehlung'), findsOneWidget);
    expect(find.text('Achtung: Moeglicher Notfall'), findsOneWidget);
    expect(find.textContaining('Notruf 112'), findsWidgets);
  });
}
