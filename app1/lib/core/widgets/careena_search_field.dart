import 'package:app1/core/themes/app_colors.dart';
import 'package:flutter/material.dart';

/// Shared Careena search input used wherever users filter visible content.
class CareenaSearchField extends StatelessWidget {
  final TextEditingController controller;
  final String hintText;
  final ValueChanged<String> onChanged;
  final bool simpleView;
  final Key? fieldKey;

  const CareenaSearchField({
    super.key,
    required this.controller,
    required this.hintText,
    required this.onChanged,
    this.simpleView = false,
    this.fieldKey,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return TextField(
      key: fieldKey,
      controller: controller,
      onChanged: onChanged,
      style: TextStyle(fontSize: simpleView ? 18 : 16),
      decoration: InputDecoration(
        hintText: hintText,
        prefixIcon: const Icon(Icons.search, color: AppColors.careenaTeal),
        suffixIcon: controller.text.isEmpty
            ? null
            : IconButton(
                tooltip: 'Suche löschen',
                onPressed: () {
                  controller.clear();
                  onChanged('');
                  FocusScope.of(context).unfocus();
                },
                icon: const Icon(Icons.close),
              ),
        filled: true,
        fillColor: isDark
            ? AppColors.darkElevatedSurface
            : AppColors.careenaBubbleBackground,
        border: _border(),
        enabledBorder: _border(),
        focusedBorder: _border(color: AppColors.careenaTeal, width: 2),
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
