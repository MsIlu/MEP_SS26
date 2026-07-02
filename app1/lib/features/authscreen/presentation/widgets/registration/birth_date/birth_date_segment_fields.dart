import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'package:app1/core/themes/app_colors.dart';
import '../../../../utils/auth_validators.dart';
import '../../../theme/auth_theme.dart';

/// Renders one visual birth date field from three focused numeric inputs.
class BirthDateSegmentFields extends StatelessWidget {
  final TextEditingController dayController;
  final TextEditingController monthController;
  final TextEditingController yearController;
  final FocusNode dayFocusNode;
  final FocusNode monthFocusNode;
  final FocusNode yearFocusNode;
  final TextEditingController birthDateController;
  final bool showValidation;
  final VoidCallback onChanged;

  const BirthDateSegmentFields({
    super.key,
    required this.dayController,
    required this.monthController,
    required this.yearController,
    required this.dayFocusNode,
    required this.monthFocusNode,
    required this.yearFocusNode,
    required this.birthDateController,
    required this.showValidation,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return FormField<String>(
      validator: (_) => AuthValidators.birthDate(birthDateController.text),
      builder: (field) {
        // Show live validation only once the user has filled all date parts.
        final liveError = showValidation
            ? AuthValidators.birthDate(birthDateController.text)
            : null;

        return InputDecorator(
          decoration: AuthTheme.inputDecoration(
            context: context,
            label: 'Geburtsdatum',
            hint: 'TT.MM.JJJJ',
          ).copyWith(errorText: field.errorText ?? liveError),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              Expanded(
                child: _BirthDateSegmentField(
                  controller: dayController,
                  focusNode: dayFocusNode,
                  hint: 'Tag',
                  maxLength: 2,
                  onCompleted: () => monthFocusNode.requestFocus(),
                  onChanged: () {
                    onChanged();
                    field.didChange(birthDateController.text);
                  },
                ),
              ),
              const _DateSeparator(),
              Expanded(
                flex: 2,
                child: _BirthDateSegmentField(
                  controller: monthController,
                  focusNode: monthFocusNode,
                  hint: 'Monat',
                  maxLength: 2,
                  onCompleted: () => yearFocusNode.requestFocus(),
                  onChanged: () {
                    onChanged();
                    field.didChange(birthDateController.text);
                  },
                ),
              ),
              const _DateSeparator(),
              Expanded(
                flex: 2,
                child: _BirthDateSegmentField(
                  controller: yearController,
                  focusNode: yearFocusNode,
                  hint: 'Jahr',
                  maxLength: 4,
                  onChanged: () {
                    onChanged();
                    field.didChange(birthDateController.text);
                  },
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}

class _BirthDateSegmentField extends StatefulWidget {
  final TextEditingController controller;
  final FocusNode focusNode;
  final String hint;
  final int maxLength;
  final VoidCallback onChanged;
  final VoidCallback? onCompleted;

  const _BirthDateSegmentField({
    required this.controller,
    required this.focusNode,
    required this.hint,
    required this.maxLength,
    required this.onChanged,
    this.onCompleted,
  });

  @override
  State<_BirthDateSegmentField> createState() => _BirthDateSegmentFieldState();
}

class _BirthDateSegmentFieldState extends State<_BirthDateSegmentField> {
  @override
  void initState() {
    super.initState();
    widget.focusNode.addListener(_normalizeOnBlur);
  }

  @override
  void didUpdateWidget(_BirthDateSegmentField oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.focusNode != widget.focusNode) {
      oldWidget.focusNode.removeListener(_normalizeOnBlur);
      widget.focusNode.addListener(_normalizeOnBlur);
    }
  }

  @override
  void dispose() {
    widget.focusNode.removeListener(_normalizeOnBlur);
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return TextFormField(
      controller: widget.controller,
      focusNode: widget.focusNode,
      keyboardType: TextInputType.number,
      textAlign: TextAlign.center,
      inputFormatters: [
        FilteringTextInputFormatter.digitsOnly,
        LengthLimitingTextInputFormatter(widget.maxLength),
      ],
      decoration: InputDecoration(
        isCollapsed: true,
        border: InputBorder.none,
        enabledBorder: InputBorder.none,
        focusedBorder: InputBorder.none,
        disabledBorder: InputBorder.none,
        errorBorder: InputBorder.none,
        focusedErrorBorder: InputBorder.none,
        contentPadding: EdgeInsets.zero,
        filled: false,
        hintText: widget.hint,
        hintStyle: TextStyle(
          color: Theme.of(context).colorScheme.onSurfaceVariant,
        ),
      ),
      style: TextStyle(color: Theme.of(context).colorScheme.onSurface),
      onChanged: (value) {
        widget.onChanged();
        if (value.length == widget.maxLength) {
          widget.onCompleted?.call();
        }
      },
    );
  }

  void _normalizeOnBlur() {
    if (widget.focusNode.hasFocus || widget.maxLength != 2) {
      return;
    }

    final value = widget.controller.text.trim();
    if (value.length != 1) {
      return;
    }

    final paddedValue = value.padLeft(2, '0');
    widget.controller.value = TextEditingValue(
      text: paddedValue,
      selection: TextSelection.collapsed(offset: paddedValue.length),
    );
    widget.onChanged();
  }
}

class _DateSeparator extends StatelessWidget {
  const _DateSeparator();

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 4),
      child: Text(
        '.',
        style: TextStyle(
          color: isDarkMode
              ? colorScheme.onSurfaceVariant
              : AppColors.careenaTitle,
          fontSize: 18,
          fontWeight: FontWeight.w800,
        ),
      ),
    );
  }
}
