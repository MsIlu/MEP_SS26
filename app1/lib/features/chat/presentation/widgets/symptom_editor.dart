import 'package:flutter/material.dart';

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

    super.dispose();
  }

  /// Adds a new empty symptom input field.
  void _addSymptomField() {
    setState(() {
      _controllers.add(TextEditingController());
    });
  }

  /// Removes one symptom field from the editor.
  void _removeSymptomField(int index) {
    setState(() {
      _controllers[index].dispose();
      _controllers.removeAt(index);
    });
  }

  /// Saves all non-empty symptoms and closes the editor.
  Future<void> _saveSymptoms() async {
    final updatedSymptoms = _controllers
        .map((controller) => controller.text.trim())
        .where((symptom) => symptom.isNotEmpty)
        .toList();

    await widget.onSave(updatedSymptoms);

    if (mounted) {
      Navigator.pop(context);
    }
  }
  @override
  Widget build(BuildContext context) {
    return Padding(
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
            const Text(
              'Erkannte Symptome bearbeiten',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 18,
                color: Color(0xFF36594F),
              ),
            ),

            const SizedBox(height: 12),

            // Scrollable symptom list with visible scrollbar for long drafts.
            Expanded(
              child: Scrollbar(
                thumbVisibility: true,
                child: SingleChildScrollView(
                  child: Column(
                    children: [
                      ..._controllers.asMap().entries.map((entry) {
                        final index = entry.key;
                        final controller = entry.value;

                        return Padding(
                          padding: const EdgeInsets.only(bottom: 8),

                          // Persistent action buttons shown below the scrollable content.
                          child: Row(
                            children: [
                              Expanded(
                                child: TextField(
                                  controller: controller,
                                  decoration: InputDecoration(
                                    labelText: 'Symptom',
                                    filled: true,
                                    fillColor: Colors.white,
                                    border: OutlineInputBorder(
                                      borderRadius: BorderRadius.circular(18),
                                      borderSide: const BorderSide(
                                        color: Color(0xFFB7CCC6),
                                        width: 1.2,
                                      ),
                                    ),

                                    enabledBorder: OutlineInputBorder(
                                      borderRadius: BorderRadius.circular(18),
                                      borderSide: const BorderSide(
                                        color: Color(0xFFB7CCC6),
                                        width: 1.2,
                                      ),
                                    ),

                                    focusedBorder: OutlineInputBorder(
                                      borderRadius: BorderRadius.circular(18),
                                      borderSide: const BorderSide(
                                        color: Color(0xFF26A69A),
                                        width: 1.5,
                                      ),
                                    ),
                                  ),
                                ),
                              ),
                              IconButton(
                                onPressed: () => _removeSymptomField(index),
                                icon: const Icon(Icons.delete_outline),
                                color: const Color(0xFF26A69A),
                              ),
                            ],
                          ),
                        );
                      }),

                      TextButton.icon(
                        onPressed: _addSymptomField,
                        icon: const Icon(Icons.add),
                        label: const Text('Symptom hinzufügen'),
                        style: TextButton.styleFrom(
                          foregroundColor: const Color(0xFF26A69A),
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
                  onPressed: _saveSymptoms,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF26A69A),
                    foregroundColor: Colors.white,
                  ),
                  child: const Text('Speichern'),
                ),
                const SizedBox(width: 8),
                TextButton(
                  onPressed: () => Navigator.pop(context),
                  style: TextButton.styleFrom(
                    foregroundColor: const Color(0xFF6E7E79),
                  ),
                  child: const Text('Abbrechen'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}