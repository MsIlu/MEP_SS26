import 'package:app1/features/chatscreen/data/models/careena_availability.dart';
import 'package:app1/features/chatscreen/presentation/widgets/chat_app_bar.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('shows limited availability with explanatory tooltip', (
    tester,
  ) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          appBar: ChatAppBar(
            onBackPressed: () {},
            onToggleTheme: () {},
            isDarkMode: false,
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
