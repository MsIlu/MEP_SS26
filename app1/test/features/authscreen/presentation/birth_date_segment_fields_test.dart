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

  testWidgets('pads single-digit day and month when focus changes', (
    tester,
  ) async {
    final dayController = TextEditingController();
    final monthController = TextEditingController();
    final yearController = TextEditingController();
    final birthDateController = TextEditingController();
    final dayFocusNode = FocusNode();
    final monthFocusNode = FocusNode();
    final yearFocusNode = FocusNode();

    void syncBirthDate() {
      birthDateController.text =
          '${dayController.text}.${monthController.text}.${yearController.text}';
    }

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
            showValidation: false,
            onChanged: syncBirthDate,
          ),
        ),
      ),
    );

    final fields = find.byType(TextField);

    await tester.enterText(fields.at(0), '2');
    await tester.tap(fields.at(1));
    await tester.pump();
    expect(dayController.text, '02');

    await tester.enterText(fields.at(1), '2');
    await tester.tap(fields.at(2));
    await tester.pump();
    expect(monthController.text, '02');

    await tester.enterText(fields.at(2), '2002');
    await tester.pump();

    expect(birthDateController.text, '02.02.2002');
  });
}
