import 'package:flutter/material.dart';

import '../../../data/dose_unit_catalog.dart';

/// Autocomplete text field for selecting common medication dose units.
class DoseUnitAutocompleteField extends StatefulWidget {
  final TextEditingController controller;

  const DoseUnitAutocompleteField({super.key, required this.controller});

  @override
  State<DoseUnitAutocompleteField> createState() =>
      _DoseUnitAutocompleteFieldState();
}

class _DoseUnitAutocompleteFieldState extends State<DoseUnitAutocompleteField> {
  final _focusNode = FocusNode();

  @override
  void dispose() {
    _focusNode.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Autocomplete<String>(
      textEditingController: widget.controller,
      focusNode: _focusNode,
      displayStringForOption: (unit) => unit,
      optionsBuilder: (textEditingValue) {
        return DoseUnitCatalog.search(textEditingValue.text);
      },
      onSelected: (unit) {
        widget.controller.text = unit;
      },
      fieldViewBuilder:
          (context, textEditingController, focusNode, onFieldSubmitted) {
            return TextFormField(
              controller: textEditingController,
              focusNode: focusNode,
              textInputAction: TextInputAction.done,
              decoration: const InputDecoration(
                labelText: 'Art',
                hintText: 'z. B. mg, Tablette, ...',
                prefixIcon: Icon(Icons.scale_outlined),
              ),
              validator: _requiredUnit,
            );
          },
    );
  }

  /// Requires a unit so amount-only doses do not become ambiguous.
  static String? _requiredUnit(String? value) {
    if (value == null || value.trim().isEmpty) {
      return 'Bitte Einheit eintragen';
    }
    return null;
  }
}
