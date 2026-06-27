import 'package:app1/core/config/app_assets.dart';
import 'package:app1/core/themes/app_colors.dart';
import 'package:flutter/material.dart';

enum BodyView { front, back }

enum BodySilhouetteSex {
  female,
  male;

  static BodySilhouetteSex fromProfileSex(String? value) {
    final normalized = value?.toLowerCase() ?? '';
    if (normalized.contains('male') || normalized.contains('männ')) {
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

  const _BodyArea(
    this.label,
    this.view,
    this.rect, {
    this.shape = _BodyAreaShape.softRect,
  });
}

enum _BodyAreaShape { oval, capsule, softRect }

const _bodyAreas = [
  _BodyArea('Kopf', BodyView.front, Rect.fromLTRB(0.425, 0.035, 0.575, 0.165),
      shape: _BodyAreaShape.oval),
  _BodyArea('Hals', BodyView.front, Rect.fromLTRB(0.455, 0.158, 0.545, 0.222),
      shape: _BodyAreaShape.oval),
  _BodyArea('Nacken', BodyView.back, Rect.fromLTRB(0.44, 0.16, 0.56, 0.235),
      shape: _BodyAreaShape.oval),
  _BodyArea('Brust', BodyView.front, Rect.fromLTRB(0.37, 0.235, 0.63, 0.365),
      shape: _BodyAreaShape.oval),
  _BodyArea('Bauch', BodyView.front, Rect.fromLTRB(0.39, 0.365, 0.61, 0.525),
      shape: _BodyAreaShape.oval),
  _BodyArea('Hüfte', BodyView.front, Rect.fromLTRB(0.38, 0.505, 0.62, 0.585),
      shape: _BodyAreaShape.oval),
  _BodyArea('Geschlechtsorgan', BodyView.front,
      Rect.fromLTRB(0.445, 0.575, 0.555, 0.655),
      shape: _BodyAreaShape.oval),
  _BodyArea('Linker Arm', BodyView.front, Rect.fromLTRB(0.17, 0.245, 0.33, 0.61),
      shape: _BodyAreaShape.capsule),
  _BodyArea('Rechter Arm', BodyView.front, Rect.fromLTRB(0.67, 0.245, 0.83, 0.61),
      shape: _BodyAreaShape.capsule),
  _BodyArea('Linker Oberschenkel', BodyView.front,
      Rect.fromLTRB(0.345, 0.61, 0.465, 0.735),
      shape: _BodyAreaShape.capsule),
  _BodyArea('Rechter Oberschenkel', BodyView.front,
      Rect.fromLTRB(0.535, 0.61, 0.655, 0.735),
      shape: _BodyAreaShape.capsule),
  _BodyArea('Linkes Knie', BodyView.front, Rect.fromLTRB(0.34, 0.715, 0.47, 0.795),
      shape: _BodyAreaShape.oval),
  _BodyArea('Rechtes Knie', BodyView.front, Rect.fromLTRB(0.53, 0.715, 0.66, 0.795),
      shape: _BodyAreaShape.oval),
  _BodyArea('Linker Fuß', BodyView.front, Rect.fromLTRB(0.34, 0.925, 0.465, 0.995),
      shape: _BodyAreaShape.oval),
  _BodyArea('Rechter Fuß', BodyView.front, Rect.fromLTRB(0.535, 0.925, 0.66, 0.995),
      shape: _BodyAreaShape.oval),
  _BodyArea('Kopf', BodyView.back, Rect.fromLTRB(0.425, 0.035, 0.575, 0.165),
      shape: _BodyAreaShape.oval),
  _BodyArea('Hals', BodyView.back, Rect.fromLTRB(0.455, 0.158, 0.545, 0.222),
      shape: _BodyAreaShape.oval),
  _BodyArea('Rücken', BodyView.back, Rect.fromLTRB(0.36, 0.235, 0.64, 0.505),
      shape: _BodyAreaShape.oval),
  _BodyArea('Hüfte', BodyView.back, Rect.fromLTRB(0.38, 0.505, 0.62, 0.585),
      shape: _BodyAreaShape.oval),
  _BodyArea('Linker Arm', BodyView.back, Rect.fromLTRB(0.17, 0.245, 0.33, 0.61),
      shape: _BodyAreaShape.capsule),
  _BodyArea('Rechter Arm', BodyView.back, Rect.fromLTRB(0.67, 0.245, 0.83, 0.61),
      shape: _BodyAreaShape.capsule),
  _BodyArea('Linker Oberschenkel', BodyView.back,
      Rect.fromLTRB(0.345, 0.61, 0.465, 0.735),
      shape: _BodyAreaShape.capsule),
  _BodyArea('Rechter Oberschenkel', BodyView.back,
      Rect.fromLTRB(0.535, 0.61, 0.655, 0.735),
      shape: _BodyAreaShape.capsule),
  _BodyArea('Linkes Knie', BodyView.back, Rect.fromLTRB(0.34, 0.715, 0.47, 0.795),
      shape: _BodyAreaShape.oval),
  _BodyArea('Rechtes Knie', BodyView.back, Rect.fromLTRB(0.53, 0.715, 0.66, 0.795),
      shape: _BodyAreaShape.oval),
  _BodyArea('Linker Fuß', BodyView.back, Rect.fromLTRB(0.34, 0.925, 0.465, 0.995),
      shape: _BodyAreaShape.oval),
  _BodyArea('Rechter Fuß', BodyView.back, Rect.fromLTRB(0.535, 0.925, 0.66, 0.995),
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
                selectedColor: AppColors.primary.withValues(alpha: 0.16),
                checkmarkColor: AppColors.primary,
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
    final normalized = Offset(
      (point.dx - rect.center.dx) / (rect.width / 2),
      (point.dy - rect.center.dy) / (rect.height / 2),
    );
    if (shape == _BodyAreaShape.oval) {
      return normalized.dx * normalized.dx + normalized.dy * normalized.dy <= 1;
    }
    return rect.contains(point);
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
    canvas.drawRRect(rounded, fill);
    canvas.drawRRect(rounded, stroke);
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
