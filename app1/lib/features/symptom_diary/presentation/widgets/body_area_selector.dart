import 'package:app1/core/themes/app_colors.dart';
import 'package:flutter/material.dart';

const _bodySilhouetteAsset =
    'assets/images/body_silhouette/body_silhouette_male_front_transparent.png';
const _bodyBackSilhouetteAsset =
    'assets/images/body_silhouette/body_silhouette_male_back_transparent.png';
const _femaleBodySilhouetteAsset =
    'assets/images/body_silhouette/body_silhouette_female_front_transparent.png';
const _femaleBodyBackSilhouetteAsset =
    'assets/images/body_silhouette/body_silhouette_female_back_transparent.png';

const _bodyAreas = [
  'Kopf',
  'Hals',
  'Brust',
  'Bauch',
  'Rücken',
  'Hüfte',
  'Knie',
  'Füße',
  'Linker Arm',
  'Rechter Arm',
  'Linkes Bein',
  'Rechtes Bein',
];

const _bodyImageAspectRatio = 768 / 1536;

/// Lets users pick the body area connected to the symptom entry.
class BodyAreaSelector extends StatelessWidget {
  final String selectedArea;
  final String? biologicalSex;
  final ValueChanged<String> onChanged;

  const BodyAreaSelector({
    super.key,
    required this.selectedArea,
    this.biologicalSex,
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
              final height = constraints.maxWidth < 360 ? 260.0 : 310.0;
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
                      ..._figureRectsFor(size).map((figure) {
                        return Positioned(
                          left: figure.rect.left,
                          top: figure.rect.top,
                          width: figure.rect.width,
                          height: figure.rect.height,
                          child: Stack(
                            fit: StackFit.expand,
                            children: [
                              Image.asset(
                                _assetForBodyView(figure.view, biologicalSex),
                                fit: BoxFit.contain,
                              ),
                            ],
                          ),
                        );
                      }),
                      Positioned(
                        left: _separatorXFor(size),
                        top: 6,
                        bottom: 30,
                        child: Container(
                          width: 1,
                          color: colorScheme.onSurfaceVariant.withValues(
                            alpha: 0.18,
                          ),
                        ),
                      ),
                      ..._figureRectsFor(size).map((figure) {
                        return Positioned(
                          left: figure.rect.left,
                          top: figure.rect.bottom + 4,
                          width: figure.rect.width,
                          child: Text(
                            _labelForBodyView(figure.view),
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              color: colorScheme.onSurfaceVariant.withValues(
                                alpha: 0.78,
                              ),
                              fontSize: 12,
                              fontWeight: FontWeight.w800,
                            ),
                          ),
                        );
                      }),
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
            children: _bodyAreas
                .map((area) {
                  final selectedAreaName = _areaNameForSelection(selectedArea);
                  final isSelected = selectedAreaName == area;
                  final selectedView = _viewForSelection(selectedArea);
                  final allowedViews = _allowedViewsForArea(area);
                  final nextView = allowedViews.contains(selectedView)
                      ? selectedView
                      : allowedViews.first;

                  return ChoiceChip(
                    label: Text(area),
                    selected: isSelected,
                    selectedColor: AppColors.careenaBubbleBackground,
                    checkmarkColor: AppColors.careenaTeal,
                    onSelected: (_) => onChanged(
                      isSelected ? '' : _valueForBodyArea(nextView, area),
                    ),
                  );
                })
                .toList(growable: false),
          ),
          const SizedBox(height: 8),
          Wrap(spacing: 8, runSpacing: 8, children: _buildBodyViewChips()),
        ],
      ),
    );
  }

  List<Widget> _buildBodyViewChips() {
    const views = [_BodyView.front, _BodyView.back];
    final selectedAreaName = _areaNameForSelection(selectedArea);
    final hasArea = selectedAreaName.isNotEmpty;

    return views
        .map((view) {
          final isAllowed =
              hasArea && _allowedViewsForArea(selectedAreaName).contains(view);
          final isSelected = hasArea && _viewForSelection(selectedArea) == view;

          return ChoiceChip(
            label: Text(_labelForBodyView(view)),
            selected: isSelected,
            selectedColor: AppColors.careenaBubbleBackground,
            checkmarkColor: AppColors.careenaTeal,
            onSelected: isAllowed
                ? (_) => onChanged(_valueForBodyArea(view, selectedAreaName))
                : null,
          );
        })
        .toList(growable: false);
  }
}

String _assetForBodyView(_BodyView view, String? biologicalSex) {
  final usesFemaleAssets = biologicalSex == 'female';

  return switch ((view, usesFemaleAssets)) {
    (_BodyView.front, true) => _femaleBodySilhouetteAsset,
    (_BodyView.back, true) => _femaleBodyBackSilhouetteAsset,
    (_BodyView.front, false) => _bodySilhouetteAsset,
    (_BodyView.back, false) => _bodyBackSilhouetteAsset,
  };
}

String _labelForBodyView(_BodyView view) {
  return switch (view) {
    _BodyView.front => 'Vorne',
    _BodyView.back => 'Hinten',
  };
}

String _valueForBodyArea(_BodyView view, String area) {
  return '${_labelForBodyView(view)}: $area';
}

List<_BodyView> _allowedViewsForArea(String area) {
  return switch (area) {
    'Bauch' => const [_BodyView.front],
    'Brust' => const [_BodyView.front],
    'Rücken' => const [_BodyView.back],
    _ => const [_BodyView.front, _BodyView.back],
  };
}

String? _bodyAreaForPosition(Offset position, Size size) {
  for (final figure in _figureRectsFor(size)) {
    if (!figure.rect.contains(position)) {
      continue;
    }

    final normalizedX = (position.dx - figure.rect.left) / figure.rect.width;
    final normalizedY = (position.dy - figure.rect.top) / figure.rect.height;

    final area = switch (figure.view) {
      _BodyView.front => _frontBodyAreaFor(normalizedX, normalizedY),
      _BodyView.back => _backBodyAreaFor(normalizedX, normalizedY),
    };
    if (area != null) {
      return _valueForBodyArea(figure.view, area);
    }
  }

  return null;
}

String? _frontBodyAreaFor(double x, double y) {
  if (_containsOval(x, y, 0.5, 0.11, 0.09, 0.08)) {
    return 'Kopf';
  }
  if (_containsRect(x, y, 0.43, 0.17, 0.57, 0.24)) {
    return 'Hals';
  }
  if (_containsRect(x, y, 0.36, 0.22, 0.64, 0.36)) {
    return 'Brust';
  }
  if (_containsRect(x, y, 0.37, 0.36, 0.63, 0.53)) {
    return 'Bauch';
  }
  if (_containsRect(x, y, 0.36, 0.50, 0.64, 0.62)) {
    return 'Hüfte';
  }
  if (_containsRect(x, y, 0.09, 0.25, 0.36, 0.58)) {
    return 'Linker Arm';
  }
  if (_containsRect(x, y, 0.64, 0.25, 0.91, 0.58)) {
    return 'Rechter Arm';
  }
  if (_containsRect(x, y, 0.35, 0.52, 0.49, 0.78)) {
    return 'Linkes Bein';
  }
  if (_containsRect(x, y, 0.51, 0.52, 0.65, 0.78)) {
    return 'Rechtes Bein';
  }
  if (_containsRect(x, y, 0.34, 0.74, 0.66, 0.84)) {
    return 'Knie';
  }
  if (_containsRect(x, y, 0.31, 0.89, 0.69, 0.98)) {
    return 'Füße';
  }

  return null;
}

String? _backBodyAreaFor(double x, double y) {
  if (_containsOval(x, y, 0.5, 0.11, 0.09, 0.08)) {
    return 'Kopf';
  }
  if (_containsRect(x, y, 0.43, 0.17, 0.57, 0.24)) {
    return 'Hals';
  }
  if (_containsRect(x, y, 0.39, 0.24, 0.61, 0.53)) {
    return 'Rücken';
  }
  if (_containsRect(x, y, 0.36, 0.50, 0.64, 0.62)) {
    return 'Hüfte';
  }
  if (_containsRect(x, y, 0.09, 0.25, 0.36, 0.58)) {
    return 'Linker Arm';
  }
  if (_containsRect(x, y, 0.64, 0.25, 0.91, 0.58)) {
    return 'Rechter Arm';
  }
  if (_containsRect(x, y, 0.35, 0.52, 0.49, 0.78)) {
    return 'Linkes Bein';
  }
  if (_containsRect(x, y, 0.51, 0.52, 0.65, 0.78)) {
    return 'Rechtes Bein';
  }
  if (_containsRect(x, y, 0.34, 0.74, 0.66, 0.84)) {
    return 'Knie';
  }
  if (_containsRect(x, y, 0.31, 0.89, 0.69, 0.98)) {
    return 'Füße';
  }

  return null;
}

List<_FigureRect> _figureRectsFor(Size size) {
  final gap = size.width < 360 ? 16.0 : 28.0;
  const labelSpace = 24.0;
  final maxFigureWidth = (size.width - gap) / 2;
  final maxFigureHeight = size.height - labelSpace;
  final figureWidth = (maxFigureHeight * _bodyImageAspectRatio).clamp(
    0.0,
    maxFigureWidth,
  );
  final figureHeight = figureWidth / _bodyImageAspectRatio;
  final top = ((size.height - labelSpace) - figureHeight) / 2;
  final left = (size.width - (figureWidth * 2) - gap) / 2;

  return [
    _FigureRect(
      view: _BodyView.front,
      rect: Rect.fromLTWH(left, top, figureWidth, figureHeight),
    ),
    _FigureRect(
      view: _BodyView.back,
      rect: Rect.fromLTWH(
        left + figureWidth + gap,
        top,
        figureWidth,
        figureHeight,
      ),
    ),
  ];
}

double _separatorXFor(Size size) {
  final figures = _figureRectsFor(size);
  if (figures.length < 2) {
    return size.width / 2;
  }

  return (figures.first.rect.right + figures.last.rect.left) / 2;
}

enum _BodyView { front, back }

class _FigureRect {
  final _BodyView view;
  final Rect rect;

  const _FigureRect({required this.view, required this.rect});
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

    final figure = _figureForSelectedArea(size, selectedArea);
    if (figure == null) {
      return;
    }

    final highlightPaint = Paint()
      ..color = AppColors.careenaTeal.withValues(alpha: 0.34)
      ..style = PaintingStyle.fill;

    final highlight = _highlightRectFor(selectedArea, figure.rect);
    if (highlight == null) {
      return;
    }

    final area = _areaNameForSelection(selectedArea);

    if (area == 'Kopf') {
      canvas.drawOval(highlight, highlightPaint);
      return;
    }

    canvas.drawRRect(
      RRect.fromRectAndRadius(highlight, const Radius.circular(18)),
      highlightPaint,
    );
  }

  _FigureRect? _figureForSelectedArea(Size size, String area) {
    final preferredView = _viewForSelection(area);

    for (final figure in _figureRectsFor(size)) {
      if (figure.view == preferredView) {
        return figure;
      }
    }

    return null;
  }

  Rect? _highlightRectFor(String area, Rect imageRect) {
    final areaName = _areaNameForSelection(area);

    return switch (areaName) {
      'Kopf' => _rectFromNormalized(imageRect, 0.41, 0.04, 0.59, 0.18),
      'Hals' => _rectFromNormalized(imageRect, 0.43, 0.17, 0.57, 0.24),
      'Brust' => _rectFromNormalized(imageRect, 0.35, 0.22, 0.65, 0.36),
      'Bauch' => _rectFromNormalized(imageRect, 0.37, 0.36, 0.63, 0.53),
      'Rücken' => _rectFromNormalized(imageRect, 0.39, 0.24, 0.61, 0.53),
      'Hüfte' => _rectFromNormalized(imageRect, 0.36, 0.50, 0.64, 0.62),
      'Knie' => _rectFromNormalized(imageRect, 0.34, 0.74, 0.66, 0.84),
      'Füße' => _rectFromNormalized(imageRect, 0.31, 0.89, 0.69, 0.98),
      'Linker Arm' => _rectFromNormalized(imageRect, 0.11, 0.25, 0.34, 0.58),
      'Rechter Arm' => _rectFromNormalized(imageRect, 0.66, 0.25, 0.89, 0.58),
      'Linkes Bein' => _rectFromNormalized(imageRect, 0.35, 0.52, 0.49, 0.78),
      'Rechtes Bein' => _rectFromNormalized(imageRect, 0.51, 0.52, 0.65, 0.78),
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

_BodyView _viewForSelection(String selection) {
  if (selection.startsWith('Hinten:')) {
    return _BodyView.back;
  }
  if (selection.startsWith('Vorne:')) {
    return _BodyView.front;
  }

  return selection == 'Rücken' ? _BodyView.back : _BodyView.front;
}

String _areaNameForSelection(String selection) {
  final separatorIndex = selection.indexOf(':');
  if (separatorIndex == -1) {
    return selection;
  }

  return selection.substring(separatorIndex + 1).trim();
}
