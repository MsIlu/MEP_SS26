import 'package:app1/core/widgets/careena_action_buttons.dart';
import 'package:app1/core/widgets/careena_snack_bar.dart';
import 'package:app1/features/authscreen/presentation/widgets/registration/registration_step_indicator.dart';
import 'package:app1/core/themes/app_colors.dart';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../../data/symptom_entry.dart';
import '../utils/symptom_body_area.dart';
import 'body_area_selector.dart';
import 'symptom_details_step.dart';
import 'symptom_selection_step.dart';

const _symptomSuggestions = [
  'Kopfschmerzen',
  'Müdigkeit',
  'Übelkeit',
  'Schwindel',
  'Husten',
  'Schmerzen',
  'Fieber',
  'Schlafprobleme',
];
const _customSymptomSuggestionsKey = 'custom_symptom_suggestions';

enum _SymptomEntryStep {
  symptom,
  bodyArea,
  details;

  String get label {
    return switch (this) {
      _SymptomEntryStep.symptom => 'Symptom',
      _SymptomEntryStep.bodyArea => 'Körper-\nstelle',
      _SymptomEntryStep.details => 'Details',
    };
  }
}

/// Coordinates the multi-step form for one symptom diary entry.
class SymptomEntryForm extends StatefulWidget {
  final Future<void> Function({
    required String symptom,
    required String bodyArea,
    required int intensity,
    double? temperatureC,
    required String note,
  })
  onSave;
  final VoidCallback? onCancel;
  final VoidCallback? onSaved;
  final String? biologicalSex;
  final String? initialSymptom;
  final SymptomEntry? initialEntry;

  /// When true and [initialSymptom] is set, skips straight to the details
  /// (intensity) step instead of stopping at body area first.
  final bool skipToDetails;

  const SymptomEntryForm({
    super.key,
    required this.onSave,
    this.onCancel,
    this.onSaved,
    this.biologicalSex,
    this.initialSymptom,
    this.initialEntry,
    this.skipToDetails = false,
  });

  @override
  State<SymptomEntryForm> createState() => _SymptomEntryFormState();
}

class _SymptomEntryFormState extends State<SymptomEntryForm> {
  final _symptomController = TextEditingController();
  final _noteController = TextEditingController();

  String _bodyArea = '';
  int _currentStepIndex = 0;
  int _intensity = 5;
  double _temperatureC = 37.0;
  // True when the original entry had a temperature or the user moved the slider.
  // Prevents persisting the 37.0 slider default for entries that never had a temperature.
  bool _temperatureExplicitlySet = true;
  List<String> _customSymptomSuggestions = [];
  bool _isSaving = false;

  @override
  void initState() {
    super.initState();
    _loadCustomSymptomSuggestions();
    final initialEntry = widget.initialEntry;
    final pre = initialEntry?.symptom ?? widget.initialSymptom;
    if (pre != null && pre.isNotEmpty) {
      _symptomController.text = pre;
      // skipToDetails: jump to the last step (intensity); the index is clamped
      // to _lastStepIndex at render time so using a large value is safe.
      _currentStepIndex = widget.skipToDetails ? 999 : 1;
    }
    if (initialEntry != null) {
      _bodyArea = initialEntry.bodyArea;
      _intensity = initialEntry.intensity;
      _temperatureC = initialEntry.temperatureC ?? 37.0;
      _temperatureExplicitlySet = initialEntry.temperatureC != null;
      _noteController.text = initialEntry.note;
      _currentStepIndex = 0;
    }
  }

  @override
  void dispose() {
    _symptomController.dispose();
    _noteController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: colorScheme.surface,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: isDarkMode
              ? colorScheme.outlineVariant.withValues(alpha: 0.55)
              : AppColors.careenaBorder,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _FormHeader(
            onCancel: widget.onCancel,
            isEditing: widget.initialEntry != null,
          ),
          const SizedBox(height: 12),
          RegistrationStepIndicator(
            currentStep: _currentStepIndex,
            labels: _stepLabels,
            onStepSelected: _selectStep,
          ),
          const SizedBox(height: 16),
          AnimatedSwitcher(
            duration: const Duration(milliseconds: 180),
            child: KeyedSubtree(
              key: ValueKey(_currentStep),
              child: _buildStepContent(),
            ),
          ),
          const SizedBox(height: 16),
          CareenaStepNavigation(
            backLabel: _isFirstStep ? 'Abbrechen' : 'Zurück',
            nextLabel: _isLastStep
                ? (widget.initialEntry == null
                      ? 'Speichern'
                      : 'Änderungen speichern')
                : 'Weiter',
            backIcon: _isFirstStep ? Icons.close : Icons.arrow_back,
            nextIcon: _isLastStep ? Icons.add : Icons.arrow_forward,
            isBusy: _isSaving,
            onBack: _isFirstStep ? widget.onCancel : _goToPreviousStep,
            onNext: _isLastStep ? _save : _goToNextStep,
          ),
        ],
      ),
    );
  }

  Widget _buildStepContent() {
    return switch (_currentStep) {
      _SymptomEntryStep.symptom => SymptomSelectionStep(
        suggestions: _allSymptomSuggestions,
        customSuggestions: _customSymptomSuggestions.toSet(),
        filteredSuggestions: _filteredSuggestions,
        controller: _symptomController,
        onChanged: _updateSymptom,
        onSelected: _selectSymptom,
        onAddCustom: _addCustomSymptomSuggestion,
        onRemoveCustom: _removeCustomSymptomSuggestion,
        onSubmitted: _goToNextStep,
      ),
      _SymptomEntryStep.bodyArea => BodyAreaSelector(
        selectedArea: _bodyArea,
        sex: BodySilhouetteSex.fromProfileSex(widget.biologicalSex),
        onChanged: (area) => setState(() => _bodyArea = area),
      ),
      _SymptomEntryStep.details => SymptomDetailsStep(
        intensity: _intensity,
        temperatureC: _temperatureC,
        useTemperature: _usesTemperature,
        noteController: _noteController,
        onIntensityChanged: (value) => setState(() => _intensity = value),
        onTemperatureChanged: (value) => setState(() {
          _temperatureC = value;
          _temperatureExplicitlySet = true;
        }),
      ),
    };
  }

  void _selectStep(int index) {
    setState(() => _currentStepIndex = index.clamp(0, _lastStepIndex));
  }

  void _goToPreviousStep() {
    setState(() => _currentStepIndex--);
  }

  void _goToNextStep() {
    if (_currentStep == _SymptomEntryStep.symptom && _symptom.isEmpty) {
      _showMissingSymptomMessage();
      return;
    }

    setState(() {
      _currentStepIndex = (_currentStepIndex + 1).clamp(0, _lastStepIndex);
    });
  }

  Future<void> _save() async {
    if (_symptom.isEmpty) {
      _showMissingSymptomMessage();
      setState(() => _currentStepIndex = 0);
      return;
    }

    setState(() => _isSaving = true);
    try {
      await widget.onSave(
        symptom: _symptom,
        bodyArea: _needsBodyArea ? _bodyArea : '',
        intensity: _intensity,
        temperatureC: _usesTemperature && _temperatureExplicitlySet ? _temperatureC : null,
        note: _noteController.text,
      );
    } catch (_) {
      if (mounted) setState(() => _isSaving = false);
      return;
    }

    if (!mounted) {
      return;
    }

    _resetForm();
    widget.onSaved?.call();
  }

  void _selectSymptom(String symptom) {
    _symptomController.text = symptom;
    _symptomController.selection = TextSelection.collapsed(
      offset: symptom.length,
    );
    _updateSymptom(symptom);
  }

  void _updateSymptom(String symptom) {
    final suggestedArea = suggestedBodyAreaForSymptom(symptom);

    setState(() {
      if (!symptomNeedsBodyArea(symptom)) {
        _bodyArea = '';
        _clampCurrentStepToActiveFlow();
        return;
      }

      if (_bodyArea.isEmpty && suggestedArea.isNotEmpty) {
        _bodyArea = suggestedArea;
      }
    });
  }

  void _resetForm() {
    _symptomController.clear();
    _noteController.clear();
    setState(() {
      _bodyArea = '';
      _currentStepIndex = 0;
      _intensity = 5;
      _temperatureC = 37.0;
      _isSaving = false;
    });
  }

  void _showMissingSymptomMessage() {
    showCareenaSnackBar(context, 'Bitte ein Symptom eintragen');
  }

  Future<void> _loadCustomSymptomSuggestions() async {
    final prefs = await SharedPreferences.getInstance();
    if (!mounted) return;

    setState(() {
      _customSymptomSuggestions =
          prefs.getStringList(_customSymptomSuggestionsKey) ?? const [];
    });
  }

  Future<void> _addCustomSymptomSuggestion() async {
    final symptom = _symptom;
    if (symptom.isEmpty || _containsSuggestion(symptom)) return;

    // Keep user-defined quick choices persistent across app starts.
    final updated = [..._customSymptomSuggestions, symptom]..sort();
    await _saveCustomSymptomSuggestions(updated);
    if (!mounted) return;
    showCareenaSnackBar(context, 'Symptom zur Auswahlliste hinzugefügt');
  }

  Future<void> _removeCustomSymptomSuggestion(String symptom) async {
    final updated = _customSymptomSuggestions
        .where((item) => item.toLowerCase() != symptom.toLowerCase())
        .toList(growable: false);
    await _saveCustomSymptomSuggestions(updated);
  }

  Future<void> _saveCustomSymptomSuggestions(List<String> suggestions) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setStringList(_customSymptomSuggestionsKey, suggestions);
    if (!mounted) return;

    setState(() => _customSymptomSuggestions = suggestions);
  }

  void _clampCurrentStepToActiveFlow() {
    if (_currentStepIndex > _lastStepIndex) {
      _currentStepIndex = _lastStepIndex;
    }
  }

  String get _symptom => _symptomController.text.trim();
  List<String> get _allSymptomSuggestions {
    return [
      ..._symptomSuggestions,
      for (final symptom in _customSymptomSuggestions)
        if (!_symptomSuggestions.any(
          (defaultSymptom) =>
              defaultSymptom.toLowerCase() == symptom.toLowerCase(),
        ))
          symptom,
    ];
  }

  bool _containsSuggestion(String symptom) {
    return _allSymptomSuggestions.any(
      (suggestion) => suggestion.toLowerCase() == symptom.toLowerCase(),
    );
  }

  bool get _needsBodyArea => symptomNeedsBodyArea(_symptom);
  bool get _usesTemperature => symptomUsesTemperature(_symptom);
  bool get _isFirstStep => _currentStepIndex == 0;
  bool get _isLastStep => _currentStepIndex >= _lastStepIndex;
  int get _lastStepIndex => _activeSteps.length - 1;

  List<String> get _stepLabels {
    return _activeSteps.map((step) => step.label).toList(growable: false);
  }

  List<_SymptomEntryStep> get _activeSteps {
    return _needsBodyArea
        ? const [
            _SymptomEntryStep.symptom,
            _SymptomEntryStep.bodyArea,
            _SymptomEntryStep.details,
          ]
        : const [_SymptomEntryStep.symptom, _SymptomEntryStep.details];
  }

  _SymptomEntryStep get _currentStep {
    return _activeSteps[_currentStepIndex.clamp(0, _lastStepIndex)];
  }

  List<String> get _filteredSuggestions {
    final query = _symptom.toLowerCase();
    if (query.isEmpty) {
      return const [];
    }

    return _allSymptomSuggestions
        .where(
          (suggestion) =>
              suggestion.toLowerCase().contains(query) &&
              suggestion != _symptom,
        )
        .toList(growable: false);
  }
}

class _FormHeader extends StatelessWidget {
  final VoidCallback? onCancel;
  final bool isEditing;

  const _FormHeader({required this.onCancel, required this.isEditing});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Row(
      children: [
        Expanded(
          child: Text(
            isEditing ? 'Symptom bearbeiten' : 'Symptom eintragen',
            style: TextStyle(
              color: colorScheme.onSurface,
              fontSize: 18,
              fontWeight: FontWeight.w800,
            ),
          ),
        ),
        if (onCancel != null)
          CareenaIconActionButton.close(
            tooltip: 'Abbrechen',
            onPressed: onCancel,
          ),
      ],
    );
  }
}
