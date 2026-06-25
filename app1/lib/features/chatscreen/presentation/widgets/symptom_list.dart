import 'package:flutter/material.dart';
import 'package:app1/core/themes/app_colors.dart';

/// Displays detected symptoms as a single compact row below the message list.
class SymptomList extends StatelessWidget {
  static const double _spacing = 8;
  static const double _chipHeight = 36;
  static const double _chipHorizontalPadding = 14;
  static const double _editChipWidth = 150;
  static const double _maxSymptomLabelWidth = 124;

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
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    final labelColor = isDarkMode
        ? colorScheme.onSurfaceVariant
        : AppColors.careenaMuted;
    final chipBackground = isDarkMode
        ? const Color(0xFF222A35)
        : const Color(0xFFF4F7F6);
    final editBackground = isDarkMode ? colorScheme.surface : Colors.white;
    final chipBorder = isDarkMode
        ? colorScheme.outlineVariant
        : const Color(0xFFB7CCC6);
    final symptomColor = isDarkMode
        ? colorScheme.onSurface
        : const Color(0xFF36594F);
    final actionColor = isDarkMode
        ? AppColors.toolbarButtonBackgroundDark
        : AppColors.careenaTeal;

    final labelStyle = TextStyle(
      color: labelColor,
      fontSize: 12,
      fontWeight: FontWeight.w500,
    );
    final symptomStyle = TextStyle(
      color: symptomColor,
      fontWeight: FontWeight.w500,
    );
    final actionStyle = TextStyle(
      color: actionColor,
      fontWeight: FontWeight.w600,
    );

    return ValueListenableBuilder<List<String>>(
      valueListenable: symptomsListenable,
      builder: (context, symptoms, child) {
        return LayoutBuilder(
          builder: (context, constraints) {
            final availableWidth = constraints.maxWidth.isFinite
                ? constraints.maxWidth
                : 820.0;
            final horizontalPadding = availableWidth < 360 ? 8.0 : 12.0;
            final rowWidth = availableWidth - (horizontalPadding * 2);
            final symptomLabelWidth = availableWidth < 420
                ? 96.0
                : _maxSymptomLabelWidth;
            final visibleCount = symptoms.isEmpty
                ? 0
                : _visibleSymptomCount(
                    context: context,
                    symptoms: symptoms,
                    rowWidth: rowWidth,
                    symptomStyle: symptomStyle,
                    actionStyle: actionStyle,
                    symptomLabelWidth: symptomLabelWidth,
                  );
            final visibleSymptoms = symptoms.take(visibleCount).toList();
            final hiddenCount = symptoms.length - visibleSymptoms.length;
            final actionLabel = symptoms.isEmpty
                ? 'Symptom hinzufügen'
                : 'Bearbeiten';
            final actionIcon = symptoms.isEmpty
                ? Icons.add
                : Icons.edit_outlined;

            return Align(
              alignment: Alignment.centerLeft,
              child: Padding(
                padding: EdgeInsets.fromLTRB(
                  horizontalPadding,
                  0,
                  horizontalPadding,
                  8,
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    if (symptoms.isNotEmpty)
                      Padding(
                        padding: const EdgeInsets.only(bottom: 6),
                        child: Text('Erkannte Symptome:', style: labelStyle),
                      ),
                    ClipRect(
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          _SymptomChip(
                            label: actionLabel,
                            icon: actionIcon,
                            labelMaxWidth: _editChipWidth,
                            foregroundColor: actionColor,
                            backgroundColor: editBackground,
                            borderColor: actionColor,
                            textStyle: actionStyle,
                            onPressed: onAddPressed,
                          ),
                          for (final symptom in visibleSymptoms) ...[
                            const SizedBox(width: _spacing),
                            Tooltip(
                              message: symptom,
                              child: _SymptomChip(
                                label: symptom,
                                labelMaxWidth: symptomLabelWidth,
                                foregroundColor: symptomColor,
                                backgroundColor: chipBackground,
                                borderColor: chipBorder,
                                textStyle: symptomStyle,
                                onPressed: () => onSymptomPressed(symptom),
                              ),
                            ),
                          ],
                          if (hiddenCount > 0) ...[
                            const SizedBox(width: _spacing),
                            _SymptomChip(
                              label: '+$hiddenCount',
                              labelMaxWidth: 52,
                              foregroundColor: actionColor,
                              backgroundColor: chipBackground,
                              borderColor: chipBorder,
                              textStyle: actionStyle,
                              onPressed: onAddPressed,
                            ),
                          ],
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }

  int _visibleSymptomCount({
    required BuildContext context,
    required List<String> symptoms,
    required double rowWidth,
    required TextStyle symptomStyle,
    required TextStyle actionStyle,
    required double symptomLabelWidth,
  }) {
    final editWidth = _editChipWidth;
    final availableWidth = rowWidth <= 0 ? 0 : rowWidth;
    var usedWidth = editWidth;
    var visibleCount = 0;

    for (var index = 0; index < symptoms.length; index += 1) {
      final hiddenAfterCandidate = symptoms.length - index - 1;
      final symptomWidth = _chipWidth(
        context: context,
        label: symptoms[index],
        style: symptomStyle,
        maxLabelWidth: symptomLabelWidth,
      );
      final moreWidth = hiddenAfterCandidate > 0
          ? _chipWidth(
              context: context,
              label: '+$hiddenAfterCandidate',
              style: actionStyle,
              maxLabelWidth: 52,
            )
          : 0.0;
      final reserveMoreWidth = moreWidth > 0 ? _spacing + moreWidth : 0.0;
      final candidateWidth =
          usedWidth + _spacing + symptomWidth + reserveMoreWidth;

      if (candidateWidth > availableWidth) {
        break;
      }

      usedWidth += _spacing + symptomWidth;
      visibleCount += 1;
    }

    return visibleCount;
  }

  double _chipWidth({
    required BuildContext context,
    required String label,
    required TextStyle style,
    required double maxLabelWidth,
  }) {
    final painter = TextPainter(
      text: TextSpan(text: label, style: style),
      maxLines: 1,
      textDirection: Directionality.of(context),
    )..layout(maxWidth: maxLabelWidth);
    final labelWidth = painter.width.clamp(0.0, maxLabelWidth).toDouble();

    return labelWidth + (_chipHorizontalPadding * 2);
  }
}

class _SymptomChip extends StatelessWidget {
  final String label;
  final IconData? icon;
  final double labelMaxWidth;
  final Color foregroundColor;
  final Color backgroundColor;
  final Color borderColor;
  final TextStyle textStyle;
  final VoidCallback onPressed;

  const _SymptomChip({
    required this.label,
    this.icon,
    required this.labelMaxWidth,
    required this.foregroundColor,
    required this.backgroundColor,
    required this.borderColor,
    required this.textStyle,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    final icon = this.icon;

    return Material(
      color: Colors.transparent,
      child: InkWell(
        borderRadius: BorderRadius.circular(9),
        onTap: onPressed,
        child: Container(
          height: SymptomList._chipHeight,
          padding: const EdgeInsets.symmetric(
            horizontal: SymptomList._chipHorizontalPadding,
          ),
          decoration: BoxDecoration(
            color: backgroundColor,
            borderRadius: BorderRadius.circular(9),
            border: Border.all(color: borderColor, width: 1.2),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              if (icon != null) ...[
                Icon(icon, size: 18, color: foregroundColor),
                const SizedBox(width: 8),
              ],
              ConstrainedBox(
                constraints: BoxConstraints(maxWidth: labelMaxWidth),
                child: Text(
                  label,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  softWrap: false,
                  style: textStyle,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
