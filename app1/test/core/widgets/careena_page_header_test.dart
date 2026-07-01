import 'package:app1/core/themes/app_colors.dart';
import 'package:app1/core/widgets/careena_page_header.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  // Test case references: documents/Testfaelle_Frontend.md#t05-core-network-und-shared-widgets
  testWidgets('centers the title between header sides', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          appBar: CareenaPageHeader(
            title: 'Seitentitel',
            onBack: () {},
            trailing: CareenaHeaderAction(
              tooltip: 'Aktion',
              icon: Icons.info_outline,
              onPressed: () {},
            ),
          ),
        ),
      ),
    );

    final titleCenter = tester.getCenter(find.text('Seitentitel'));
    final screenCenter = tester.getCenter(find.byType(Scaffold)).dx;

    expect(titleCenter.dx, closeTo(screenCenter, 0.1));
  });

  testWidgets('uses the subtle centralized header background without divider', (
    tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(appBar: CareenaPageHeader(title: 'Seitentitel')),
      ),
    );

    final appBar = tester.widget<AppBar>(find.byType(AppBar));

    expect(appBar.backgroundColor, AppColors.headerBackgroundLight);
    expect(find.byType(Divider), findsNothing);
  });

  testWidgets('uses compact title when full title does not fit', (
    tester,
  ) async {
    await tester.binding.setSurfaceSize(const Size(360, 720));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          appBar: CareenaPageHeader(
            title: 'Willkommen Alexanderthegreat!',
            compactTitle: 'Willkommen!',
            showBack: false,
            leading: CareenaHeaderAction(
              tooltip: 'Guide',
              icon: Icons.help_outline,
              onPressed: () {},
            ),
            trailing: CareenaHeaderAction(
              tooltip: 'Profil',
              icon: Icons.person_outline,
              onPressed: () {},
            ),
          ),
        ),
      ),
    );

    expect(find.text('Willkommen Alexanderthegreat!'), findsNothing);
    expect(find.text('Willkommen!'), findsOneWidget);
  });

  testWidgets('hides first name on narrow home header', (tester) async {
    await tester.binding.setSurfaceSize(const Size(320, 720));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          appBar: CareenaPageHeader(
            title: 'Willkommen Emilia!',
            compactTitle: 'Willkommen!',
            showBack: false,
            leading: CareenaHeaderAction(
              tooltip: 'Guide',
              icon: Icons.help_outline,
              onPressed: () {},
            ),
            trailing: CareenaHeaderAction(
              tooltip: 'Profil',
              icon: Icons.person_outline,
              onPressed: () {},
            ),
          ),
        ),
      ),
    );

    expect(find.text('Willkommen Emilia!'), findsNothing);
    expect(find.text('Willkommen!'), findsOneWidget);
  });
}
