import 'package:app1/features/authscreen/presentation/widgets/registration/birth_date/birth_date_segment_fields.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('birth date segment inputs have no individual borders', (
    tester,
  ) async {
    final dayController = TextEditingController(text: '03');
    final monthController = TextEditingController(text: '05');
    final yearController = TextEditingController(text: '2004');
    final birthDateController = TextEditingController(text: '03.05.2004');
    final dayFocusNode = FocusNode();
    final monthFocusNode = FocusNode();
    final yearFocusNode = FocusNode();

    addTearDown(dayController.dispose);
    addTearDown(monthController.dispose);
    addTearDown(yearController.dispose);
    addTearDown(birthDateController.dispose);
    addTearDown(dayFocusNode.dispose);
    addTearDown(monthFocusNode.dispose);
    addTearDown(yearFocusNode.dispose);

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: BirthDateSegmentFields(
            dayController: dayController,
            monthController: monthController,
            yearController: yearController,
            dayFocusNode: dayFocusNode,
            monthFocusNode: monthFocusNode,
            yearFocusNode: yearFocusNode,
            birthDateController: birthDateController,
            showValidation: true,
            onChanged: () {},
          ),
        ),
      ),
    );

    final fields = tester.widgetList<TextField>(find.byType(TextField));
    expect(fields, hasLength(3));

    for (final field in fields) {
      final decoration = field.decoration;
      expect(decoration, isNotNull);
      expect(decoration?.border, InputBorder.none);
      expect(decoration?.enabledBorder, InputBorder.none);
      expect(decoration?.focusedBorder, InputBorder.none);
      expect(decoration?.errorBorder, InputBorder.none);
      expect(decoration?.focusedErrorBorder, InputBorder.none);
    }
  });
}
