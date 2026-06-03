import 'package:app1/features/chatscreen/presentation/themes/app_colors.dart';
import 'package:flutter/material.dart';

const _bodySilhouetteAsset = 'assets/images/body_silhouette_transparent.png';

const _bodyAreas = [
  'Kopf',
  'Brust',
  'Bauch',
  'Rücken',
  'Linker Arm',
  'Rechter Arm',
  'Linkes Bein',
  'Rechtes Bein',
];

/// Lets users pick the body area connected to the symptom entry.
class BodyAreaSelector extends StatelessWidget {
  final String selectedArea;
  final ValueChanged<String> onChanged;

  const BodyAreaSelector({
    super.key,
    required this.selectedArea,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: isDarkMode
            ? colorScheme.surfaceContainerHighest.withValues(alpha: 0.35)
            : AppColors.careenaBubbleBackground.withValues(alpha: 0.45),
        borderRadius: BorderRadius.circular(18),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  'Wo tut es weh?',
                  style: TextStyle(
                    color: colorScheme.onSurface,
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ),
              Text(
                selectedArea.isEmpty ? 'optional' : selectedArea,
                style: const TextStyle(
                  color: AppColors.careenaTeal,
                  fontSize: 12,
                  fontWeight: FontWeight.w800,
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          LayoutBuilder(
            builder: (context, constraints) {
              final height = constraints.maxWidth < 360 ? 280.0 : 320.0;
              final size = Size(constraints.maxWidth, height);

              return GestureDetector(
                behavior: HitTestBehavior.opaque,
                onTapDown: (details) {
                  final area = _bodyAreaForPosition(
                    details.localPosition,
                    size,
                  );
                  if (area != null) {
                    onChanged(selectedArea == area ? '' : area);
                  }
                },
                child: SizedBox(
                  height: size.height,
                  child: Stack(
                    fit: StackFit.expand,
                    children: [
                      Image.asset(_bodySilhouetteAsset, fit: BoxFit.contain),
                      CustomPaint(
                        painter: _BodyAreaHighlightPainter(
                          selectedArea: selectedArea,
                        ),
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
          const SizedBox(height: 10),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: _bodyAreas.map((area) {
              final isSelected = selectedArea == area;

              return ChoiceChip(
                label: Text(area),
                selected: isSelected,
                selectedColor: AppColors.careenaBubbleBackground,
                checkmarkColor: AppColors.careenaTeal,
                onSelected: (_) => onChanged(isSelected ? '' : area),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }
}

String? _bodyAreaForPosition(Offset position, Size size) {
  final imageRect = _imageRectFor(size);
  if (!imageRect.contains(position)) {
    return null;
  }

  final normalizedX = (position.dx - imageRect.left) / imageRect.width;
  final normalizedY = (position.dy - imageRect.top) / imageRect.height;

  if (_containsOval(normalizedX, normalizedY, 0.5, 0.11, 0.09, 0.08)) {
    return 'Kopf';
  }
  if (_containsRect(normalizedX, normalizedY, 0.36, 0.22, 0.64, 0.36)) {
    return 'Brust';
  }
  if (_containsRect(normalizedX, normalizedY, 0.37, 0.36, 0.63, 0.53)) {
    return 'Bauch';
  }
  if (_containsRect(normalizedX, normalizedY, 0.41, 0.24, 0.59, 0.53)) {
    return 'Rücken';
  }
  if (_containsRect(normalizedX, normalizedY, 0.09, 0.25, 0.36, 0.58)) {
    return 'Linker Arm';
  }
  if (_containsRect(normalizedX, normalizedY, 0.64, 0.25, 0.91, 0.58)) {
    return 'Rechter Arm';
  }
  if (_containsRect(normalizedX, normalizedY, 0.34, 0.52, 0.49, 0.95)) {
    return 'Linkes Bein';
  }
  if (_containsRect(normalizedX, normalizedY, 0.51, 0.52, 0.66, 0.95)) {
    return 'Rechtes Bein';
  }

  return null;
}

Rect _imageRectFor(Size size) {
  const imageAspectRatio = 768 / 1536;
  final availableAspectRatio = size.width / size.height;

  if (availableAspectRatio > imageAspectRatio) {
    final imageWidth = size.height * imageAspectRatio;
    final left = (size.width - imageWidth) / 2;
    return Rect.fromLTWH(left, 0, imageWidth, size.height);
  }

  final imageHeight = size.width / imageAspectRatio;
  final top = (size.height - imageHeight) / 2;
  return Rect.fromLTWH(0, top, size.width, imageHeight);
}

bool _containsRect(
  double x,
  double y,
  double left,
  double top,
  double right,
  double bottom,
) {
  return x >= left && x <= right && y >= top && y <= bottom;
}

bool _containsOval(
  double x,
  double y,
  double centerX,
  double centerY,
  double radiusX,
  double radiusY,
) {
  final normalizedDx = (x - centerX) / radiusX;
  final normalizedDy = (y - centerY) / radiusY;
  return normalizedDx * normalizedDx + normalizedDy * normalizedDy <= 1;
}

class _BodyAreaHighlightPainter extends CustomPainter {
  final String selectedArea;

  const _BodyAreaHighlightPainter({required this.selectedArea});

  @override
  void paint(Canvas canvas, Size size) {
    if (selectedArea.isEmpty) {
      return;
    }

    final imageRect = _imageRectFor(size);
    final highlightPaint = Paint()
      ..color = AppColors.careenaTeal.withValues(alpha: 0.34)
      ..style = PaintingStyle.fill;

    final highlight = _highlightRectFor(selectedArea, imageRect);
    if (highlight == null) {
      return;
    }

    if (selectedArea == 'Kopf') {
      canvas.drawOval(highlight, highlightPaint);
      return;
    }

    canvas.drawRRect(
      RRect.fromRectAndRadius(highlight, const Radius.circular(18)),
      highlightPaint,
    );
  }

  Rect? _highlightRectFor(String area, Rect imageRect) {
    return switch (area) {
      'Kopf' => _rectFromNormalized(imageRect, 0.41, 0.04, 0.59, 0.18),
      'Brust' => _rectFromNormalized(imageRect, 0.35, 0.22, 0.65, 0.36),
      'Bauch' => _rectFromNormalized(imageRect, 0.37, 0.36, 0.63, 0.53),
      'Rücken' => _rectFromNormalized(imageRect, 0.41, 0.24, 0.59, 0.53),
      'Linker Arm' => _rectFromNormalized(imageRect, 0.11, 0.25, 0.34, 0.58),
      'Rechter Arm' => _rectFromNormalized(imageRect, 0.66, 0.25, 0.89, 0.58),
      'Linkes Bein' => _rectFromNormalized(imageRect, 0.34, 0.52, 0.49, 0.95),
      'Rechtes Bein' => _rectFromNormalized(imageRect, 0.51, 0.52, 0.66, 0.95),
      _ => null,
    };
  }

  Rect _rectFromNormalized(
    Rect imageRect,
    double left,
    double top,
    double right,
    double bottom,
  ) {
    return Rect.fromLTRB(
      imageRect.left + left * imageRect.width,
      imageRect.top + top * imageRect.height,
      imageRect.left + right * imageRect.width,
      imageRect.top + bottom * imageRect.height,
    );
  }

  @override
  bool shouldRepaint(_BodyAreaHighlightPainter oldDelegate) {
    return oldDelegate.selectedArea != selectedArea;
  }
}