import 'package:flutter/material.dart';
import 'package:app1/core/themes/app_colors.dart';

/// Bottom sheet used to edit, remove and save detected symptoms.
class SymptomEditor extends StatefulWidget {
  final List<String> symptoms;
  final Future<void> Function(List<String> updatedSymptoms) onSave;

  const SymptomEditor({
    super.key,
    required this.symptoms,
    required this.onSave,
  });

  @override
  State<SymptomEditor> createState() => _SymptomEditorState();
}

class _SymptomEditorState extends State<SymptomEditor> {
  late List<TextEditingController> _controllers;
  final ScrollController _scrollController = ScrollController();
  bool _isSaving = false;

  @override
  void initState() {
    super.initState();

    _controllers = widget.symptoms
        .map((symptom) => TextEditingController(text: symptom))
        .toList();
  }

  @override
  void dispose() {
    for (final controller in _controllers) {
      controller.dispose();
    }
    _scrollController.dispose();

    super.dispose();
  }

  void _addSymptomField() {
    setState(() {
      _controllers.add(TextEditingController());
    });
  }

  void _removeSymptomField(int index) {
    setState(() {
      _controllers[index].dispose();
      _controllers.removeAt(index);
    });
  }

  Future<void> _saveSymptoms() async {
    setState(() => _isSaving = true);

    final updatedSymptoms = _controllers
        .map((controller) => controller.text.trim())
        .where((symptom) => symptom.isNotEmpty)
        .toList();

    try {
      await widget.onSave(updatedSymptoms);
    } finally {
      if (mounted) {
        setState(() => _isSaving = false);
      }
    }

    if (mounted) {
      Navigator.pop(context);
    }
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    final backgroundColor = isDarkMode
        ? colorScheme.surface
        : AppColors.symptomEditorSurfaceLight;
    final titleColor = isDarkMode
        ? colorScheme.onSurface
        : AppColors.symptomEditorText;
    final fieldColor = isDarkMode ? AppColors.darkElevatedSurface : AppColors.white;
    final borderColor = isDarkMode
        ? colorScheme.outlineVariant
        : AppColors.symptomEditorBorder;
    final actionColor = isDarkMode
        ? AppColors.toolbarButtonBackgroundDark
        : AppColors.careenaTeal;

    return DecoratedBox(
      decoration: BoxDecoration(color: backgroundColor),
      child: Padding(
        padding: EdgeInsets.fromLTRB(
          16,
          16,
          16,
          MediaQuery.of(context).viewInsets.bottom + 16,
        ),
        child: SizedBox(
          height: MediaQuery.of(context).size.height * 0.75,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Erkannte Symptome bearbeiten',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 18,
                  color: titleColor,
                ),
              ),
              const SizedBox(height: 12),
              Expanded(
                child: Scrollbar(
                  controller: _scrollController,
                  thumbVisibility: true,
                  child: SingleChildScrollView(
                    controller: _scrollController,
                    primary: false,
                    child: Column(
                      children: [
                        ..._controllers.asMap().entries.map((entry) {
                          final index = entry.key;
                          final controller = entry.value;

                          return Padding(
                            padding: const EdgeInsets.only(bottom: 8),
                            child: Row(
                              children: [
                                Expanded(
                                  child: TextField(
                                    controller: controller,
                                    style: TextStyle(
                                      color: colorScheme.onSurface,
                                    ),
                                    decoration: InputDecoration(
                                      labelText: 'Symptom',
                                      filled: true,
                                      fillColor: fieldColor,
                                      border: OutlineInputBorder(
                                        borderRadius: BorderRadius.circular(18),
                                        borderSide: BorderSide(
                                          color: borderColor,
                                          width: 1.2,
                                        ),
                                      ),
                                      enabledBorder: OutlineInputBorder(
                                        borderRadius: BorderRadius.circular(18),
                                        borderSide: BorderSide(
                                          color: borderColor,
                                          width: 1.2,
                                        ),
                                      ),
                                      focusedBorder: OutlineInputBorder(
                                        borderRadius: BorderRadius.circular(18),
                                        borderSide: BorderSide(
                                          color: actionColor,
                                          width: 1.5,
                                        ),
                                      ),
                                    ),
                                  ),
                                ),
                                IconButton(
                                  onPressed: _isSaving
                                      ? null
                                      : () => _removeSymptomField(index),
                                  icon: const Icon(Icons.delete_outline),
                                  color: actionColor,
                                ),
                              ],
                            ),
                          );
                        }),
                        TextButton.icon(
                          onPressed: _isSaving ? null : _addSymptomField,
                          icon: const Icon(Icons.add),
                          label: const Text('Symptom hinzufügen'),
                          style: TextButton.styleFrom(
                            foregroundColor: actionColor,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  ElevatedButton(
                    onPressed: _isSaving ? null : _saveSymptoms,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: actionColor,
                      foregroundColor: AppColors.white,
                    ),
                    child: Text(_isSaving ? 'Speichern...' : 'Speichern'),
                  ),
                  const SizedBox(width: 8),
                  TextButton(
                    onPressed: _isSaving ? null : () => Navigator.pop(context),
                    style: TextButton.styleFrom(
                      foregroundColor: isDarkMode
                          ? colorScheme.onSurfaceVariant
                          : AppColors.symptomEditorMuted,
                    ),
                    child: const Text('Abbrechen'),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
