import 'package:flutter/material.dart';

import '../../common/auth_info_widgets.dart';
import 'birth_date_segment_fields.dart';

const double _birthDateAgeGap = 10;
const String _ageInfoText =
    'Dein Alter berechnet sich aus dem eingegebenen Geburtsdatum und dient zu deiner Überprüfung.';

/// Places the editable birth date input next to the derived age preview.
class BirthDateFieldWithAge extends StatelessWidget {
  final TextEditingController dayController;
  final TextEditingController monthController;
  final TextEditingController yearController;
  final TextEditingController ageController;
  final FocusNode dayFocusNode;
  final FocusNode monthFocusNode;
  final FocusNode yearFocusNode;
  final TextEditingController birthDateController;
  final bool showValidation;
  final VoidCallback onChanged;

  const BirthDateFieldWithAge({
    super.key,
    required this.dayController,
    required this.monthController,
    required this.yearController,
    required this.ageController,
    required this.dayFocusNode,
    required this.monthFocusNode,
    required this.yearFocusNode,
    required this.birthDateController,
    required this.showValidation,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final birthDateFields = BirthDateSegmentFields(
          dayController: dayController,
          monthController: monthController,
          yearController: yearController,
          dayFocusNode: dayFocusNode,
          monthFocusNode: monthFocusNode,
          yearFocusNode: yearFocusNode,
          birthDateController: birthDateController,
          showValidation: showValidation,
          onChanged: onChanged,
        );
        final ageField = AuthCalculatedField(
          controller: ageController,
          label: 'Alter',
          hint: 'automatisch berechnet',
          infoText: _ageInfoText,
        );

        if (constraints.maxWidth < 420) {
          return Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              birthDateFields,
              const SizedBox(height: _birthDateAgeGap),
              ageField,
            ],
          );
        }

        return Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(child: birthDateFields),
            const SizedBox(width: _birthDateAgeGap),
            Expanded(child: ageField),
          ],
        );
      },
    );
  }
}
