import 'package:app1/core/widgets/responsive_frame.dart';
import 'package:flutter/material.dart';

import '../../../data/medication_catalog_item.dart';
import '../../../data/medication_schedule.dart';
import 'medication_form_card.dart';

/// Dialog that owns add-medication form state and delegates saving upward.
class MedicationFormDialog extends StatefulWidget {
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

  const MedicationFormDialog({super.key, required this.onSave});

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

  @override
  void initState() {
    super.initState();
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
      backgroundColor: Colors.transparent,
      child: SingleChildScrollView(
        child: ResponsiveFrame(
          maxWidth: 720,
          padding: EdgeInsets.only(
            bottom: MediaQuery.viewInsetsOf(context).bottom,
          ),
          child: MedicationFormCard(
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

    await widget.onSave(
      _nameController.text,
      _formattedDose,
      _selectedTime,
      _frequency == MedicationFrequency.twiceDaily ? _secondSelectedTime : null,
      _frequency,
      _remindersEnabled,
      _selectedCatalogItem,
    );

    if (mounted) {
      Navigator.pop(context, true);
    }
  }

  /// Stores metadata from the demo catalog while keeping the text field editable.
  void _selectCatalogItem(MedicationCatalogItem item) {
    setState(() => _selectedCatalogItem = item);
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
}