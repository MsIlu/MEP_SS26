import 'package:app1/core/themes/app_colors.dart';
import 'package:flutter/material.dart';

/// Shared Careena search input used wherever users filter visible content.
class CareenaSearchField extends StatelessWidget {
  final TextEditingController controller;
  final String hintText;
  final ValueChanged<String> onChanged;
  final bool simpleView;
  final Key? fieldKey;
  final Color? fillColor;

  const CareenaSearchField({
    super.key,
    required this.controller,
    required this.hintText,
    required this.onChanged,
    this.simpleView = false,
    this.fieldKey,
    this.fillColor,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final colorScheme = Theme.of(context).colorScheme;

    return TextField(
      key: fieldKey,
      controller: controller,
      onChanged: onChanged,
      style: TextStyle(
        color: colorScheme.onSurface,
        fontSize: simpleView ? 18 : 16,
      ),
      decoration: InputDecoration(
        hintText: hintText,
        hintStyle: TextStyle(color: colorScheme.onSurface),
        prefixIcon: Icon(Icons.search, color: colorScheme.onSurface),
        suffixIcon: controller.text.isEmpty
            ? null
            : IconButton(
                tooltip: 'Suche löschen',
                onPressed: () {
                  controller.clear();
                  onChanged('');
                  FocusScope.of(context).unfocus();
                },
                icon: Icon(Icons.close, color: colorScheme.onSurface),
              ),
        filled: true,
        fillColor:
            fillColor ??
            (isDark
                ? AppColors.darkElevatedSurface
                : AppColors.careenaBubbleBackground),
        border: _border(),
        enabledBorder: _border(),
        focusedBorder: _border(color: AppColors.greyShade400, width: 2),
      ),
    );
  }

  OutlineInputBorder _border({Color? color, double width = 0}) {
    return OutlineInputBorder(
      borderRadius: BorderRadius.circular(16),
      borderSide: color == null
          ? BorderSide.none
          : BorderSide(color: color, width: width),
    );
  }
}
