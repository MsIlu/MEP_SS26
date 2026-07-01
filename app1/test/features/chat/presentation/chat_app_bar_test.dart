import 'package:app1/features/chatscreen/data/models/careena_availability.dart';
import 'package:app1/features/chatscreen/presentation/widgets/chat_app_bar.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('defaults to checking availability instead of online', (
    tester,
  ) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(appBar: ChatAppBar(onBackPressed: () {})),
      ),
    );

    expect(find.text('Careena'), findsOneWidget);
    expect(find.text('prüft...'), findsOneWidget);
    expect(find.byTooltip('Careena prüft die Verbindung.'), findsOneWidget);
  });

  testWidgets('shows limited availability with explanatory tooltip', (
    tester,
  ) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          appBar: ChatAppBar(
            onBackPressed: () {},
            availability: CareenaAvailability.limited,
          ),
        ),
      ),
    );

    expect(find.text('Careena'), findsOneWidget);
    expect(find.text('eingeschränkt'), findsOneWidget);
    expect(
      find.byTooltip(
        'Careena ist erreichbar, aber Antworten können aktuell verzögert oder eingeschränkt sein.',
      ),
      findsOneWidget,
    );
  });
}
