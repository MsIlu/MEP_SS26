import 'package:app1/features/authscreen/presentation/widgets/common/auth_layout.dart';
import 'package:app1/features/authscreen/presentation/widgets/registration/registration_step_indicator.dart';
import 'package:app1/core/widgets/careena_page_header.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('step connectors are centered on all progress circles', (
    tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: SizedBox(
            width: 540,
            child: RegistrationStepIndicator(currentStep: 1),
          ),
        ),
      ),
    );

    final circleCenters = [
      for (var index = 0; index < 3; index++)
        tester.getCenter(
          find.byKey(ValueKey('registration-step-circle-$index')),
        ),
    ];
    final connectorCenters = [
      for (var index = 0; index < 2; index++)
        tester.getCenter(
          find.byKey(ValueKey('registration-step-connector-$index')),
        ),
    ];

    expect(connectorCenters[0].dy, circleCenters[0].dy);
    expect(connectorCenters[1].dy, circleCenters[1].dy);
    expect(
      connectorCenters[0].dx,
      (circleCenters[0].dx + circleCenters[1].dx) / 2,
    );
    expect(
      connectorCenters[1].dx,
      (circleCenters[1].dx + circleCenters[2].dx) / 2,
    );
  });

  testWidgets('fixed auth header keeps title between equal action buttons', (
    tester,
  ) async {
    await tester.pumpWidget(
      MaterialApp(
        home: AuthPageScaffold(
          fixedHeader: CareenaPageHeader(
            title: 'Konto erstellen',
            onBack: () {},
            trailing: CareenaHeaderAction(
              tooltip: 'Darkmode aktivieren',
              icon: Icons.dark_mode,
              onPressed: () {},
            ),
          ),
          child: const SizedBox(height: 1200),
        ),
      ),
    );

    final titleCenter = tester.getCenter(find.text('Konto erstellen'));
    final backCenter = tester.getCenter(find.byIcon(Icons.arrow_back));
    final themeCenter = tester.getCenter(find.byIcon(Icons.dark_mode));

    expect(titleCenter.dx, closeTo((backCenter.dx + themeCenter.dx) / 2, 0.1));

    await tester.drag(
      find.byType(SingleChildScrollView),
      const Offset(0, -400),
    );
    await tester.pump();

    expect(tester.getCenter(find.text('Konto erstellen')).dy, titleCenter.dy);
  });
}
