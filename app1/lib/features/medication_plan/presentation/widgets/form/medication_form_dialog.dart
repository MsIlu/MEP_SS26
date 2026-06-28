import 'package:app1/core/themes/app_colors.dart';
import 'package:app1/core/widgets/responsive_frame.dart';
import 'package:app1/core/network/api_exception.dart';
import 'package:flutter/material.dart';

import '../../../data/medication_catalog_item.dart';
import '../../../data/medication_entry.dart';
import '../../../data/medication_schedule.dart';
import 'medication_form_card.dart';

/// Dialog that owns add-medication form state and delegates saving upward.
class MedicationFormDialog extends StatefulWidget {
  final MedicationEntry? initialEntry;
  final Future<void> Function(
    String name,
    String dose,
    TimeOfDay intakeTime,
    TimeOfDay? secondIntakeTime,
    MedicationFrequency frequency,
    bool remindersEnabled,
    MedicationCatalogItem? catalogItem,
  )
  onSave;

  const MedicationFormDialog({
    super.key,
    this.initialEntry,
    required this.onSave,
  });

  @override
  State<MedicationFormDialog> createState() => _MedicationFormDialogState();
}

class _MedicationFormDialogState extends State<MedicationFormDialog> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _nameFocusNode = FocusNode();
  final _doseAmountController = TextEditingController();
  final _doseUnitController = TextEditingController();

  MedicationCatalogItem? _selectedCatalogItem;
  TimeOfDay _selectedTime = const TimeOfDay(hour: 8, minute: 0);
  TimeOfDay _secondSelectedTime = const TimeOfDay(hour: 20, minute: 0);
  MedicationFrequency _frequency = MedicationFrequency.daily;
  bool _remindersEnabled = true;
  bool _isSaving = false;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _prefillFromInitialEntry();
    _nameController.addListener(_clearCatalogSelectionForManualInput);
  }

  @override
  void dispose() {
    _nameController.removeListener(_clearCatalogSelectionForManualInput);
    _nameFocusNode.dispose();
    _nameController.dispose();
    _doseAmountController.dispose();
    _doseUnitController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      insetPadding: const EdgeInsets.all(18),
      backgroundColor: AppColors.transparent,
      child: SingleChildScrollView(
        child: ResponsiveFrame(
          maxWidth: 720,
          padding: EdgeInsets.only(
            bottom: MediaQuery.viewInsetsOf(context).bottom,
          ),
          child: MedicationFormCard(
            title: widget.initialEntry == null
                ? 'Neues Medikament'
                : 'Medikament bearbeiten',
            submitLabel: widget.initialEntry == null
                ? 'Eintrag speichern'
                : 'Änderungen speichern',
            submitIcon: widget.initialEntry == null ? Icons.add : Icons.check,
            isSubmitting: _isSaving,
            errorMessage: _errorMessage,
            formKey: _formKey,
            nameController: _nameController,
            nameFocusNode: _nameFocusNode,
            doseAmountController: _doseAmountController,
            doseUnitController: _doseUnitController,
            selectedTime: _selectedTime,
            secondSelectedTime: _secondSelectedTime,
            frequency: _frequency,
            remindersEnabled: _remindersEnabled,
            selectedCatalogItem: _selectedCatalogItem,
            onCatalogItemSelected: _selectCatalogItem,
            onTimeTap: _pickTime,
            onSecondTimeTap: _pickSecondTime,
            onFrequencyChanged: (value) {
              setState(() => _frequency = value);
            },
            onReminderChanged: (value) {
              setState(() => _remindersEnabled = value);
            },
            onCancel: () => Navigator.pop(context, false),
            onSubmit: _saveEntry,
          ),
        ),
      ),
    );
  }

  /// Uses a 24-hour picker so the selected intake time matches German UI copy.
  Future<void> _pickTime() async {
    final pickedTime = await _pickTimeWithInitialValue(_selectedTime);
    if (pickedTime != null) {
      setState(() => _selectedTime = pickedTime);
    }
  }

  /// Opens the second 24-hour picker used by twice-daily schedules.
  Future<void> _pickSecondTime() async {
    final pickedTime = await _pickTimeWithInitialValue(_secondSelectedTime);
    if (pickedTime != null) {
      setState(() => _secondSelectedTime = pickedTime);
    }
  }

  /// Wraps Flutter's time picker with the app's 24-hour display preference.
  Future<TimeOfDay?> _pickTimeWithInitialValue(TimeOfDay initialTime) {
    return showTimePicker(
      context: context,
      initialTime: initialTime,
      builder: (context, child) {
        return MediaQuery(
          data: MediaQuery.of(context).copyWith(alwaysUse24HourFormat: true),
          child: child!,
        );
      },
    );
  }

  /// Validates the form, persists through the parent, and closes the dialog.
  Future<void> _saveEntry() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() {
      _isSaving = true;
      _errorMessage = null;
    });

    try {
      await widget.onSave(
        _nameController.text,
        _formattedDose,
        _selectedTime,
        _frequency == MedicationFrequency.twiceDaily
            ? _secondSelectedTime
            : null,
        _frequency,
        _remindersEnabled,
        _selectedCatalogItem,
      );

      if (mounted) {
        Navigator.pop(context, true);
      }
    } catch (error) {
      if (mounted) {
        setState(() {
          _errorMessage = _saveErrorMessage(error);
        });
      }
    } finally {
      if (mounted) {
        setState(() => _isSaving = false);
      }
    }
  }

  String _saveErrorMessage(Object error) {
    if (error is ApiException && error.statusCode == 409) {
      return 'Dieses Medikament ist bereits in deinem Medikationsplan vorhanden.';
    }

    return 'Medikament konnte nicht gespeichert werden. Bitte erneut versuchen.';
  }

  /// Stores metadata from the demo catalog while keeping the text field editable.
  void _selectCatalogItem(MedicationCatalogItem item) {
    setState(() => _selectedCatalogItem = item);
  }

  /// Initializes the form with the selected medication when editing.
  void _prefillFromInitialEntry() {
    final entry = widget.initialEntry;
    if (entry == null) {
      return;
    }

    final parsedDose = _parseDose(entry.dose);
    _nameController.text = entry.name;
    _doseAmountController.text = parsedDose.amount;
    _doseUnitController.text = parsedDose.unit;
    _selectedTime = entry.intakeTime;
    _secondSelectedTime =
        entry.secondIntakeTime ?? const TimeOfDay(hour: 20, minute: 0);
    _frequency = entry.frequency;
    _remindersEnabled = entry.remindersEnabled;
    _selectedCatalogItem = entry.catalogItem;
  }

  /// Drops catalog metadata once the user changes the selected medication name.
  void _clearCatalogSelectionForManualInput() {
    final selectedItem = _selectedCatalogItem;
    if (selectedItem == null || _nameController.text == selectedItem.name) {
      return;
    }

    setState(() => _selectedCatalogItem = null);
  }

  /// Joins amount and unit into the persisted dose display text.
  String get _formattedDose {
    return '${_doseAmountController.text.trim()} ${_doseUnitController.text.trim()}';
  }

  _ParsedDose _parseDose(String dose) {
    final normalized = dose.trim();
    final separatorIndex = normalized.indexOf(' ');

    if (separatorIndex == -1) {
      return _ParsedDose(amount: normalized, unit: '');
    }

    return _ParsedDose(
      amount: normalized.substring(0, separatorIndex).trim(),
      unit: normalized.substring(separatorIndex + 1).trim(),
    );
  }
}

class _ParsedDose {
  final String amount;
  final String unit;

  const _ParsedDose({required this.amount, required this.unit});
}
