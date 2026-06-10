import 'package:flutter/material.dart';
import '../../utils/medical_terms.dart';
import 'package:app1/core/themes/app_colors.dart';

/// Inline explanation box for a detected medical term in an assistant message.
class MedicalTermInfoBox extends StatelessWidget {
  /// Glossary entry to display.
  final MedicalTerm term;

  const MedicalTermInfoBox({super.key, required this.term});

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: 'Erklärung des medizinischen Fachbegriffs ${term.term}',
      child: Container(
        margin: const EdgeInsets.only(top: 10),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: AppColors.careenaBubbleBackground,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: AppColors.careenaInfoBorder),
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Icon(
              Icons.info_outline,
              color: AppColors.careenaTeal,
              size: 18,
            ),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                '${term.term}: ${term.explanation}',
                style: const TextStyle(
                  color: AppColors.careenaDark,
                  fontSize: 13,
                  height: 1.35,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
