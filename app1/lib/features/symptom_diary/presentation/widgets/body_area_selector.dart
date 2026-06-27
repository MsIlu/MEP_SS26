import 'package:app1/core/config/app_assets.dart';
import 'package:app1/core/themes/app_colors.dart';
import 'dart:math' as math;
import 'package:flutter/material.dart';

enum BodyView { front, back }

enum BodySilhouetteSex {
  female,
  male;

  static BodySilhouetteSex fromProfileSex(String? value) {
    final normalized = value?.trim().toLowerCase() ?? '';
    if (normalized == 'male' ||
        normalized == 'männlich' ||
        normalized == 'maennlich') {
      return BodySilhouetteSex.male;
    }
    return BodySilhouetteSex.female;
  }
}

class _BodyArea {
  final String label;
  final BodyView view;
  final Rect rect;
  final _BodyAreaShape shape;
  final double angle;

  const _BodyArea(
    this.label,
    this.view,
    this.rect, {
    this.shape = _BodyAreaShape.softRect,
    this.angle = 0,
  });
}

enum _BodyAreaShape { oval, capsule, softRect }

const _areaLift = 0.035;

Rect _areaRect(double left, double top, double right, double bottom) {
  return Rect.fromLTRB(left, top - _areaLift, right, bottom - _areaLift);
}

final _bodyAreas = [
  _BodyArea('Kopf', BodyView.front, _areaRect(0.425, 0.045, 0.575, 0.175),
      shape: _BodyAreaShape.oval),
  _BodyArea('Hals', BodyView.front, _areaRect(0.455, 0.158, 0.545, 0.222),
      shape: _BodyAreaShape.oval),
  _BodyArea('Nacken', BodyView.back, _areaRect(0.44, 0.16, 0.56, 0.235),
      shape: _BodyAreaShape.oval),
  _BodyArea('Brust', BodyView.front, _areaRect(0.38, 0.215, 0.62, 0.335),
      shape: _BodyAreaShape.oval),
  _BodyArea('Bauch', BodyView.front, _areaRect(0.405, 0.335, 0.595, 0.475),
      shape: _BodyAreaShape.oval),
  _BodyArea('Hüfte', BodyView.front, _areaRect(0.36, 0.435, 0.64, 0.515),
      shape: _BodyAreaShape.oval),
  _BodyArea('Geschlechtsorgan', BodyView.front,
      _areaRect(0.455, 0.49, 0.545, 0.565),
      shape: _BodyAreaShape.oval),
  _BodyArea('Linker Arm', BodyView.front, _areaRect(0.25, 0.235, 0.32, 0.555),
      shape: _BodyAreaShape.capsule, angle: 10),
  _BodyArea('Rechter Arm', BodyView.front, _areaRect(0.68, 0.235, 0.75, 0.555),
      shape: _BodyAreaShape.capsule, angle: -10),
  _BodyArea('Linker Oberschenkel', BodyView.front,
      _areaRect(0.375, 0.515, 0.475, 0.665),
      shape: _BodyAreaShape.capsule),
  _BodyArea('Rechter Oberschenkel', BodyView.front,
      _areaRect(0.525, 0.515, 0.625, 0.665),
      shape: _BodyAreaShape.capsule),
  _BodyArea('Linkes Knie', BodyView.front, _areaRect(0.365, 0.66, 0.47, 0.725),
      shape: _BodyAreaShape.oval),
  _BodyArea('Rechtes Knie', BodyView.front, _areaRect(0.53, 0.66, 0.635, 0.725),
      shape: _BodyAreaShape.oval),
  _BodyArea('Linker Fuß', BodyView.front, _areaRect(0.365, 0.86, 0.465, 0.935),
      shape: _BodyAreaShape.oval),
  _BodyArea('Rechter Fuß', BodyView.front, _areaRect(0.535, 0.86, 0.635, 0.935),
      shape: _BodyAreaShape.oval),
  _BodyArea('Kopf', BodyView.back, _areaRect(0.425, 0.045, 0.575, 0.175),
      shape: _BodyAreaShape.oval),
  _BodyArea('Rücken', BodyView.back, _areaRect(0.37, 0.215, 0.63, 0.475),
      shape: _BodyAreaShape.oval),
  _BodyArea('Hüfte', BodyView.back, _areaRect(0.36, 0.435, 0.64, 0.515),
      shape: _BodyAreaShape.oval),
  _BodyArea('Linker Arm', BodyView.back, _areaRect(0.25, 0.235, 0.32, 0.555),
      shape: _BodyAreaShape.capsule, angle: 10),
  _BodyArea('Rechter Arm', BodyView.back, _areaRect(0.68, 0.235, 0.75, 0.555),
      shape: _BodyAreaShape.capsule, angle: -10),
  _BodyArea('Linker Oberschenkel', BodyView.back,
      _areaRect(0.375, 0.515, 0.475, 0.665),
      shape: _BodyAreaShape.capsule),
  _BodyArea('Rechter Oberschenkel', BodyView.back,
      _areaRect(0.525, 0.515, 0.625, 0.665),
      shape: _BodyAreaShape.capsule),
  _BodyArea('Linkes Knie', BodyView.back, _areaRect(0.365, 0.66, 0.47, 0.725),
      shape: _BodyAreaShape.oval),
  _BodyArea('Rechtes Knie', BodyView.back, _areaRect(0.53, 0.66, 0.635, 0.725),
      shape: _BodyAreaShape.oval),
  _BodyArea('Linker Fuß', BodyView.back, _areaRect(0.365, 0.86, 0.465, 0.935),
      shape: _BodyAreaShape.oval),
  _BodyArea('Rechter Fuß', BodyView.back, _areaRect(0.535, 0.86, 0.635, 0.935),
      shape: _BodyAreaShape.oval),
];

/// Lets users pick the body area connected to the symptom entry.
class BodyAreaSelector extends StatefulWidget {
  final String selectedArea;
  final ValueChanged<String> onChanged;
  final BodySilhouetteSex sex;

  const BodyAreaSelector({
    super.key,
    required this.selectedArea,
    required this.onChanged,
    this.sex = BodySilhouetteSex.female,
  });

  @override
  State<BodyAreaSelector> createState() => _BodyAreaSelectorState();
}

class _BodyAreaSelectorState extends State<BodyAreaSelector> {
  BodyView _view = BodyView.front;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    final areas = _areasForView(_view);

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
                widget.selectedArea.isEmpty ? 'optional' : widget.selectedArea,
                style: const TextStyle(
                  color: AppColors.primary,
                  fontSize: 12,
                  fontWeight: FontWeight.w800,
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          SegmentedButton<BodyView>(
            style: ButtonStyle(
              backgroundColor: WidgetStateProperty.resolveWith((states) {
                if (states.contains(WidgetState.selected)) {
                  return AppColors.primary;
                }
                return AppColors.transparent;
              }),
              foregroundColor: WidgetStateProperty.resolveWith((states) {
                if (states.contains(WidgetState.selected)) {
                  return AppColors.white;
                }
                return colorScheme.onSurface;
              }),
              iconColor: WidgetStateProperty.resolveWith((states) {
                if (states.contains(WidgetState.selected)) {
                  return AppColors.white;
                }
                return AppColors.primary;
              }),
            ),
            segments: const [
              ButtonSegment(value: BodyView.front, label: Text('Vorne')),
              ButtonSegment(value: BodyView.back, label: Text('Hinten')),
            ],
            selected: {_view},
            onSelectionChanged: (selection) {
              setState(() => _view = selection.first);
              if (!_areasForView(selection.first)
                  .any((area) => area.label == widget.selectedArea)) {
                widget.onChanged('');
              }
            },
          ),
          const SizedBox(height: 10),
          LayoutBuilder(
            builder: (context, constraints) {
              final height = constraints.maxWidth < 360 ? 280.0 : 320.0;
              final size = Size(constraints.maxWidth, height);

              return GestureDetector(
                behavior: HitTestBehavior.opaque,
                onTapDown: (details) => _selectAt(details.localPosition, size),
                child: SizedBox(
                  height: size.height,
                  child: Stack(
                    fit: StackFit.expand,
                    children: [
                      Image.asset(_assetFor(widget.sex, _view),
                          fit: BoxFit.contain),
                      CustomPaint(
                        painter: _BodyAreaHighlightPainter(
                          selectedArea: widget.selectedArea,
                          view: _view,
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
            children: areas.map((area) {
              final isSelected = widget.selectedArea == area.label;

              return ChoiceChip(
                label: Text(area.label),
                selected: isSelected,
                selectedColor: AppColors.primary,
                checkmarkColor: AppColors.white,
                labelStyle: TextStyle(
                  color: isSelected ? AppColors.white : colorScheme.onSurface,
                  fontWeight: isSelected ? FontWeight.w800 : FontWeight.w600,
                ),
                onSelected: (_) =>
                    widget.onChanged(isSelected ? '' : area.label),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }

  void _selectAt(Offset position, Size size) {
    final imageRect = _imageRectFor(size);
    if (!imageRect.contains(position)) return;

    final normalized = Offset(
      (position.dx - imageRect.left) / imageRect.width,
      (position.dy - imageRect.top) / imageRect.height,
    );
    final area = _areasForView(_view).cast<_BodyArea?>().firstWhere(
          (area) => area!._contains(normalized),
          orElse: () => null,
        );

    if (area != null) {
      widget.onChanged(widget.selectedArea == area.label ? '' : area.label);
    }
  }
}

List<_BodyArea> _areasForView(BodyView view) {
  return _bodyAreas.where((area) => area.view == view).toList(growable: false);
}

String _assetFor(BodySilhouetteSex sex, BodyView view) {
  return switch ((sex, view)) {
    (BodySilhouetteSex.male, BodyView.front) => AppAssets.bodyMaleFront,
    (BodySilhouetteSex.male, BodyView.back) => AppAssets.bodyMaleBack,
    (BodySilhouetteSex.female, BodyView.front) => AppAssets.bodyFemaleFront,
    (BodySilhouetteSex.female, BodyView.back) => AppAssets.bodyFemaleBack,
  };
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

extension on _BodyArea {
  bool _contains(Offset point) {
    final localPoint = _rotateAround(point, rect.center, -angle);
    final normalized = Offset(
      (localPoint.dx - rect.center.dx) / (rect.width / 2),
      (localPoint.dy - rect.center.dy) / (rect.height / 2),
    );
    if (shape == _BodyAreaShape.oval) {
      return normalized.dx * normalized.dx + normalized.dy * normalized.dy <= 1;
    }
    return rect.contains(localPoint);
  }

  Offset _rotateAround(Offset point, Offset center, double degrees) {
    if (degrees == 0) return point;

    final radians = degrees * math.pi / 180;
    final translated = point - center;
    return Offset(
      center.dx +
          translated.dx * math.cos(radians) -
          translated.dy * math.sin(radians),
      center.dy +
          translated.dx * math.sin(radians) +
          translated.dy * math.cos(radians),
    );
  }
}

class _BodyAreaHighlightPainter extends CustomPainter {
  final String selectedArea;
  final BodyView view;

  const _BodyAreaHighlightPainter({
    required this.selectedArea,
    required this.view,
  });

  @override
  void paint(Canvas canvas, Size size) {
    if (selectedArea.isEmpty) return;

    final area = _areasForView(view)
        .cast<_BodyArea?>()
        .firstWhere((area) => area!.label == selectedArea, orElse: () => null);
    if (area == null) return;

    final imageRect = _imageRectFor(size);
    final highlight = _scaleRect(area.rect, imageRect);
    final fill = Paint()
      ..color = AppColors.primary.withValues(alpha: 0.32)
      ..style = PaintingStyle.fill;
    final stroke = Paint()
      ..color = AppColors.white.withValues(alpha: 0.9)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2;

    if (area.shape == _BodyAreaShape.oval) {
      canvas.drawOval(highlight, fill);
      canvas.drawOval(highlight, stroke);
      return;
    }

    final radius = area.shape == _BodyAreaShape.capsule
        ? Radius.circular(highlight.shortestSide / 2)
        : const Radius.circular(24);
    final rounded = RRect.fromRectAndRadius(highlight, radius);
    canvas.save();
    if (area.angle != 0) {
      canvas.translate(highlight.center.dx, highlight.center.dy);
      canvas.rotate(area.angle * math.pi / 180);
      canvas.translate(-highlight.center.dx, -highlight.center.dy);
    }
    canvas.drawRRect(rounded, fill);
    canvas.drawRRect(rounded, stroke);
    canvas.restore();
  }

  Rect _scaleRect(Rect rect, Rect imageRect) {
    return Rect.fromLTRB(
      imageRect.left + rect.left * imageRect.width,
      imageRect.top + rect.top * imageRect.height,
      imageRect.left + rect.right * imageRect.width,
      imageRect.top + rect.bottom * imageRect.height,
    );
  }

  @override
  bool shouldRepaint(_BodyAreaHighlightPainter oldDelegate) {
    return oldDelegate.selectedArea != selectedArea || oldDelegate.view != view;
  }
}
