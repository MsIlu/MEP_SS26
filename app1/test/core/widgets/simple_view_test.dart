import 'package:app1/core/widgets/simple_view.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('simple view exposes app-wide larger defaults', (tester) async {
    late bool scopeEnabled;
    late MediaQueryData mediaQuery;
    late ThemeData theme;

    await tester.pumpWidget(
      MaterialApp(
        home: SimpleViewAppDefaults(
          enabled: true,
          child: Builder(
            builder: (context) {
              scopeEnabled = SimpleViewScope.isEnabled(context);
              mediaQuery = MediaQuery.of(context);
              theme = Theme.of(context);
              return const Scaffold(body: Text('Simple view'));
            },
          ),
        ),
      ),
    );

    expect(scopeEnabled, isTrue);
    expect(mediaQuery.textScaler.scale(1), greaterThan(1));
    expect(theme.listTileTheme.minTileHeight, 72);
    expect(
      theme.iconButtonTheme.style?.minimumSize?.resolve({}),
      const Size.square(56),
    );
    expect(
      theme.filledButtonTheme.style?.minimumSize?.resolve({}),
      const Size(64, 58),
    );
  });
}
