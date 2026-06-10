import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'package:app1/core/themes/app_colors.dart';
import '../../../data/registration_condition_options.dart';
import '../../../utils/auth_validators.dart';
import '../../../utils/bmi_utils.dart';
import '../../theme/auth_theme.dart';
import '../common/auth_buttons.dart';
import '../common/auth_fields.dart';
import '../common/auth_info_widgets.dart';
import '../common/auth_layout.dart';

final _heightInputFormatters = [
  FilteringTextInputFormatter.digitsOnly,
  LengthLimitingTextInputFormatter(3),
];

final _weightInputFormatters = [_WeightInputFormatter()];
const String _bmiInfoText =
    'Der BMI wird automatisch aus Größe und Gewicht berechnet und dient nur als grobe Orientierung. Er berücksichtigt nicht: dein Bewegungslevel, Schwangerschaft, oder anderes.';

/// Second registration step: health context used for personalization.
class RegistrationHealthDataStep extends StatefulWidget {
  final GlobalKey<FormState> formKey;
  final String selectedSex;
  final Set<String> selectedConditions;
  final TextEditingController heightController;
  final TextEditingController weightController;
  final TextEditingController notesController;
  final ValueChanged<String> onSexChanged;
  final void Function(String condition, bool selected) onConditionChanged;
  final VoidCallback onNext;

  const RegistrationHealthDataStep({
    super.key,
    required this.formKey,
    required this.selectedSex,
    required this.selectedConditions,
    required this.heightController,
    required this.weightController,
    required this.notesController,
    required this.onSexChanged,
    required this.onConditionChanged,
    required this.onNext,
  });

  @override
  State<RegistrationHealthDataStep> createState() =>
      _RegistrationHealthDataStepState();
}

class _RegistrationHealthDataStepState
    extends State<RegistrationHealthDataStep> {
  late final TextEditingController _bmiController;

  @override
  void initState() {
    super.initState();
    _bmiController = TextEditingController();
    widget.heightController.addListener(_refreshBmi);
    widget.weightController.addListener(_refreshBmi);
    _refreshBmi();
  }

  @override
  void didUpdateWidget(RegistrationHealthDataStep oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.heightController != widget.heightController) {
      oldWidget.heightController.removeListener(_refreshBmi);
      widget.heightController.addListener(_refreshBmi);
    }
    if (oldWidget.weightController != widget.weightController) {
      oldWidget.weightController.removeListener(_refreshBmi);
      widget.weightController.addListener(_refreshBmi);
    }
    _refreshBmi();
  }

  @override
  void dispose() {
    widget.heightController.removeListener(_refreshBmi);
    widget.weightController.removeListener(_refreshBmi);
    _bmiController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    final helperTextColor = isDarkMode
        ? colorScheme.onSurfaceVariant
        : AppColors.careenaMuted;

    return Form(
      key: widget.formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const AuthSectionTitle('Gesundheitsangaben'),
          const SizedBox(height: 16),
          _BirthSexSelector(
            selectedSex: widget.selectedSex,
            onChanged: widget.onSexChanged,
          ),
          const SizedBox(height: 16),
          AdaptiveFieldRow(
            children: [
              AuthTextField(
                controller: widget.heightController,
                label: 'Größe',
                hint: 'z.B. 170',
                keyboardType: TextInputType.number,
                textInputAction: TextInputAction.next,
                inputFormatters: _heightInputFormatters,
                suffixText: 'cm',
                validator: AuthValidators.heightCm,
              ),
              AuthTextField(
                controller: widget.weightController,
                label: 'Gewicht',
                hint: 'z.B. 70,5',
                keyboardType: const TextInputType.numberWithOptions(
                  decimal: true,
                ),
                inputFormatters: _weightInputFormatters,
                suffixText: 'kg',
                validator: AuthValidators.weightKg,
              ),
            ],
          ),
          const SizedBox(height: 10),
          AuthCalculatedField(
            controller: _bmiController,
            label: 'BMI',
            hint: 'automatisch berechnet',
            infoText: _bmiInfoText,
          ),
          const SizedBox(height: 20),
          Text(
            'Vorerkrankungen (optional)',
            style: AuthTheme.sectionTitleStyle(context).copyWith(fontSize: 16),
          ),
          const SizedBox(height: 8),
          Text(
            'Wähle alle zutreffenden aus.',
            style: TextStyle(color: helperTextColor),
          ),
          const SizedBox(height: 10),
          _ConditionChips(
            selectedConditions: widget.selectedConditions,
            onChanged: widget.onConditionChanged,
          ),
          const SizedBox(height: 18),
          AuthTextField(
            controller: widget.notesController,
            label: 'Weitere Informationen (optional)',
            hint: 'z.B. Medikamente, Operationen, Sonstiges ...',
            maxLength: 300,
            maxLines: 4,
          ),
          const SizedBox(height: 12),
          CareenaButton(text: 'Weiter', onPressed: widget.onNext),
        ],
      ),
    );
  }

  void _refreshBmi() {
    final bmi = BmiUtils.calculate(
      heightCm: widget.heightController.text,
      weightKg: widget.weightController.text,
    );
    _bmiController.text = bmi == null ? '' : BmiUtils.format(bmi);
  }
}

class _BirthSexSelector extends StatelessWidget {
  final String selectedSex;
  final ValueChanged<String> onChanged;

  const _BirthSexSelector({required this.selectedSex, required this.onChanged});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    final containerColor = isDarkMode
        ? AppColors.darkElevatedSurface
        : Colors.white;

    final borderColor = isDarkMode
        ? colorScheme.outlineVariant
        : AppColors.careenaBorder;

    final segmentedBackground = isDarkMode
        ? AppColors.segmentedControlBackgroundDark
        : AppColors.careenaNoteBackground;

    final segmentedSelectedBackground = isDarkMode
        ? AppColors.chatInputAccentDark
        : AppColors.careenaSoftAccent;

    final segmentedForeground = isDarkMode
        ? colorScheme.onSurfaceVariant
        : AppColors.careenaBody;

    final segmentedSelectedForeground = isDarkMode
        ? Colors.white
        : AppColors.careenaTitle;

    return DecoratedBox(
      decoration: BoxDecoration(
        color: containerColor,
        border: Border.all(color: borderColor),
        borderRadius: BorderRadius.circular(AuthTheme.fieldRadius),
      ),
      child: Padding(
        padding: const EdgeInsets.fromLTRB(16, 12, 16, 14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Row(
              children: [
                Expanded(child: _BirthSexLabel()),
                SizedBox(width: 8),
                _BirthSexInfoButton(),
              ],
            ),
            const SizedBox(height: 10),
            SegmentedButton<String>(
              segments: const [
                ButtonSegment(
                  value: 'Weiblich',
                  label: Text('weiblich'),
                  icon: Icon(Icons.female_outlined),
                ),
                ButtonSegment(
                  value: 'Männlich',
                  label: Text('männlich'),
                  icon: Icon(Icons.male_outlined),
                ),
              ],
              selected: {selectedSex},
              showSelectedIcon: false,
              style: SegmentedButton.styleFrom(
                backgroundColor: segmentedBackground,
                foregroundColor: segmentedForeground,
                selectedBackgroundColor: segmentedSelectedBackground,
                selectedForegroundColor: segmentedSelectedForeground,
                side: BorderSide(color: borderColor),
              ),
              onSelectionChanged: (selection) => onChanged(selection.first),
            ),
          ],
        ),
      ),
    );
  }
}

class _BirthSexLabel extends StatelessWidget {
  const _BirthSexLabel();

  @override
  Widget build(BuildContext context) {
    return Text(
      'Geburtsgeschlecht',
      style: AuthTheme.sectionTitleStyle(context).copyWith(fontSize: 16),
    );
  }
}

class _BirthSexInfoButton extends StatelessWidget {
  static const String _message =
      'Bitte gib das Geschlecht an, mit dem du geboren wurdest. Diese Information kann für bestimmte geschlechtsbezogene Erkrankungen und medizinische Einschätzungen wichtig sein.';

  const _BirthSexInfoButton();

  @override
  Widget build(BuildContext context) {
    return const AuthInfoButton(
      title: 'Geburtsgeschlecht',
      message: _message,
      visualDensity: VisualDensity.compact,
    );
  }
}

class _ConditionChips extends StatelessWidget {
  final Set<String> selectedConditions;
  final void Function(String condition, bool selected) onChanged;

  const _ConditionChips({
    required this.selectedConditions,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    final chipBackground = isDarkMode ? AppColors.darkElevatedSurface : null;

    final selectedChipBackground = isDarkMode
        ? AppColors.chatInputAccentDark
        : AppColors.careenaSoftAccent;

    final chipTextColor = isDarkMode
        ? colorScheme.onSurface
        : AppColors.careenaDark;

    final checkmarkColor = isDarkMode ? Colors.white : AppColors.careenaTitle;

    final borderColor = isDarkMode
        ? colorScheme.outlineVariant
        : AppColors.careenaBorder;

    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: [
        for (final condition in registrationConditionOptions)
          FilterChip(
            label: Text(condition, style: TextStyle(color: chipTextColor)),
            selected: selectedConditions.contains(condition),
            backgroundColor: chipBackground,
            selectedColor: selectedChipBackground,
            checkmarkColor: checkmarkColor,
            side: BorderSide(color: borderColor),
            onSelected: (selected) => onChanged(condition, selected),
          ),
      ],
    );
  }
}

class _WeightInputFormatter extends TextInputFormatter {
  final RegExp _validWeight = RegExp(r'^\d*([,.]\d{0,3})?$');

  @override
  TextEditingValue formatEditUpdate(
    TextEditingValue oldValue,
    TextEditingValue newValue,
  ) {
    if (_validWeight.hasMatch(newValue.text)) {
      return newValue;
    }
    return oldValue;
  }
}
