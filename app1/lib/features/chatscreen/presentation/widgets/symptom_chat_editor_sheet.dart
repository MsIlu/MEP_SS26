import 'package:app1/core/themes/app_colors.dart';
import 'package:app1/features/symptom_diary/data/symptom_import.dart';
import 'package:app1/features/symptom_diary/presentation/widgets/symptom_entry_form.dart';
import 'package:flutter/material.dart';

/// Bottom sheet for editing chat symptoms using the same form as the diary.
///
/// Each symptom can be edited via [SymptomEntryForm] (name → body area →
/// intensity), deleted, or new ones added. Changes are reported immediately
/// via [onChanged].
class SymptomChatEditorSheet extends StatefulWidget {
  final List<SymptomImport> symptoms;
  final String? biologicalSex;
  final void Function(List<SymptomImport> updated) onChanged;

  const SymptomChatEditorSheet({
    super.key,
    required this.symptoms,
    required this.onChanged,
    this.biologicalSex,
  });

  @override
  State<SymptomChatEditorSheet> createState() => _SymptomChatEditorSheetState();
}

class _SymptomChatEditorSheetState extends State<SymptomChatEditorSheet> {
  late List<SymptomImport> _symptoms;

  @override
  void initState() {
    super.initState();
    _symptoms = List<SymptomImport>.from(widget.symptoms);
  }

  void _delete(int index) {
    setState(() => _symptoms.removeAt(index));
    widget.onChanged(_symptoms);
  }

  Future<void> _editOrAdd({int? editIndex}) async {
    final existing = editIndex != null ? _symptoms[editIndex] : null;

    await showDialog<void>(
      context: context,
      builder: (dialogContext) {
        return Dialog(
          insetPadding: const EdgeInsets.all(18),
          backgroundColor: AppColors.transparent,
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 640),
            child: SingleChildScrollView(
              child: SymptomEntryForm(
                initialSymptom: existing?.name,
                skipToDetails: existing != null,
                biologicalSex: widget.biologicalSex,
                onSave: ({
                  required String symptom,
                  required String bodyArea,
                  required int intensity,
                  double? temperatureC,
                  required String note,
                }) async {
                  final updated = SymptomImport(
                    name: symptom,
                    severity: intensity,
                    bodyArea: bodyArea.isEmpty ? null : bodyArea,
                  );
                  setState(() {
                    if (editIndex != null) {
                      _symptoms[editIndex] = updated;
                    } else {
                      _symptoms.add(updated);
                    }
                  });
                  widget.onChanged(_symptoms);
                },
                onCancel: () => Navigator.pop(dialogContext),
                onSaved: () => Navigator.pop(dialogContext),
              ),
            ),
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    final actionColor = isDarkMode
        ? AppColors.toolbarButtonBackgroundDark
        : AppColors.careenaTeal;
    final bgColor = isDarkMode
        ? colorScheme.surface
        : AppColors.symptomEditorSurfaceLight;

    return DecoratedBox(
      decoration: BoxDecoration(color: bgColor),
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
                  color: isDarkMode
                      ? colorScheme.onSurface
                      : AppColors.symptomEditorText,
                ),
              ),
              const SizedBox(height: 12),
              Expanded(
                child: ListView.builder(
                  itemCount: _symptoms.length + 1,
                  itemBuilder: (context, index) {
                    if (index == _symptoms.length) {
                      return TextButton.icon(
                        onPressed: () => _editOrAdd(),
                        icon: const Icon(Icons.add),
                        label: const Text('Symptom hinzufügen'),
                        style: TextButton.styleFrom(
                          foregroundColor: actionColor,
                        ),
                      );
                    }

                    final imp = _symptoms[index];
                    final subtitle = _buildSubtitle(imp);

                    return ListTile(
                      contentPadding: EdgeInsets.zero,
                      title: Text(imp.name),
                      subtitle: subtitle != null
                          ? Text(subtitle, style: const TextStyle(fontSize: 12))
                          : null,
                      trailing: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          IconButton(
                            icon: const Icon(Icons.edit_outlined),
                            color: actionColor,
                            tooltip: 'Bearbeiten',
                            onPressed: () => _editOrAdd(editIndex: index),
                          ),
                          IconButton(
                            icon: const Icon(Icons.delete_outline),
                            color: actionColor,
                            tooltip: 'Entfernen',
                            onPressed: () => _delete(index),
                          ),
                        ],
                      ),
                    );
                  },
                ),
              ),
              Align(
                alignment: Alignment.centerRight,
                child: TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: const Text('Fertig'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  String? _buildSubtitle(SymptomImport imp) {
    final parts = <String>[];
    if (imp.bodyArea != null && imp.bodyArea!.isNotEmpty) {
      parts.add(imp.bodyArea!);
    }
    if (imp.severity != null) {
      parts.add('Intensität: ${imp.severity}/10');
    }
    return parts.isEmpty ? null : parts.join(' · ');
  }
}
