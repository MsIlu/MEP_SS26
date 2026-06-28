import 'package:app1/features/chatscreen/presentation/dialogs/leave_chat.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  // Test case references: documents/Testfaelle_Frontend.md#t06-chat-core-und-ui
  const defaultMessage =
      'Wenn du fortfährst, gelangst du zurück zur Startseite. '
      'Der aktuelle Chat wird nicht gespeichert.';

  Future<void> pumpDialogLauncher(
    WidgetTester tester, {
    String? message,
    String? confirmLabel,
  }) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: Builder(
            builder: (context) {
              return TextButton(
                onPressed: () {
                  if (message == null && confirmLabel == null) {
                    showLeaveChatDialog(context);
                    return;
                  }

                  showLeaveChatDialog(
                    context,
                    message: message ?? defaultMessage,
                    confirmLabel: confirmLabel ?? 'Zur Startseite',
                  );
                },
                child: const Text('Dialog öffnen'),
              );
            },
          ),
        ),
      ),
    );

    await tester.tap(find.text('Dialog öffnen'));
    await tester.pumpAndSettle();
  }

  testWidgets('shows homescreen copy by default', (tester) async {
    await pumpDialogLauncher(tester);

    expect(find.text('Zur Startseite'), findsOneWidget);
    expect(find.textContaining('zurück zur Startseite'), findsOneWidget);
  });

  testWidgets('shows custom destination copy', (tester) async {
    await pumpDialogLauncher(
      tester,
      message: 'Wenn du fortfährst, gelangst du zurück zur Startseite. '
          'Der aktuelle Chat wird nicht gespeichert.',
      confirmLabel: 'Zur Startseite',
    );

    expect(find.text('Zur Startseite'), findsOneWidget);
    expect(find.textContaining('zurück zur Startseite'), findsOneWidget);
  });
}
