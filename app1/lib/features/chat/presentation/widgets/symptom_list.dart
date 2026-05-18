import 'package:flutter/material.dart';

/// Displays detected symptoms as compact chips below the smart replies.
/// Only the edit chip opens the editor overlay.
class SymptomList extends StatelessWidget {
  final ValueNotifier<List<String>> symptomsListenable;
  final VoidCallback onAddPressed;
  final void Function(String symptom) onSymptomPressed;

  const SymptomList({
    super.key,
    required this.symptomsListenable,
    required this.onAddPressed,
    required this.onSymptomPressed,
  });

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<List<String>>(
      valueListenable: symptomsListenable,
      builder: (context, symptoms, child) {
        if (symptoms.isEmpty) {
          return const SizedBox.shrink();
        }

        // Limits the visible symptom chips to keep the chat UI compact.
        final visibleSymptoms = symptoms.take(3).toList();

        // Remaining symptoms are grouped into a "+X" chip.
        final hiddenCount = symptoms.length - visibleSymptoms.length;

        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            const Padding(
              padding: EdgeInsets.only(left: 12, right: 8, bottom: 2),
              child: Text(
                'Erkannte Symptome:',
                style: TextStyle(
                  color: Color(0xFF7A7A7A),
                  fontSize: 12,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
            SizedBox(
              width: double.infinity,
              height: 52,
              child: ListView.separated(
                padding: const EdgeInsets.fromLTRB(12, 6, 12, 6),
                scrollDirection: Axis.horizontal,
                itemCount:
                visibleSymptoms.length + 1 + (hiddenCount > 0 ? 1 : 0),
                separatorBuilder: (context, index) =>
                const SizedBox(width: 8),
                itemBuilder: (context, index) {
                  // Opens the symptom editor bottom sheet.
                  if (index == 0) {
                    return ActionChip(
                      avatar: const Icon(
                        Icons.edit_outlined,
                        size: 18,
                        color: Color(0xFF26A69A),
                      ),
                      label: const Text('Bearbeiten'),
                      backgroundColor: Colors.white,
                      labelStyle: const TextStyle(
                        color: Color(0xFF26A69A),
                        fontWeight: FontWeight.w600,
                      ),
                      side: const BorderSide(
                        color: Color(0xFF26A69A),
                      ),
                      onPressed: onAddPressed,
                    );
                  }

                  if (hiddenCount > 0 &&
                      index == visibleSymptoms.length + 1) {
                    return ActionChip(
                      label: Text('+$hiddenCount'),
                      backgroundColor: const Color(0xFFF4F7F6),
                      labelStyle: const TextStyle(
                        color: Color(0xFF26A69A),
                        fontWeight: FontWeight.w600,
                      ),
                      side: const BorderSide(
                        color: Color(0xFFB7CCC6),
                      ),
                      onPressed: onAddPressed,
                    );
                  }

                  final symptom = visibleSymptoms[index - 1];

                  // Read-only symptom chip shown to the user.
                  return Chip(
                    visualDensity: VisualDensity.compact,
                    materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                    label: Text(symptom),
                    backgroundColor: const Color(0xFFF4F7F6),
                    labelStyle: const TextStyle(
                      color: Color(0xFF36594F),
                      fontWeight: FontWeight.w500,
                    ),
                    side: const BorderSide(
                      color: Color(0xFFB7CCC6),
                    ),
                  );
                },
              ),
            ),
          ],
        );
      },
    );
  }
}