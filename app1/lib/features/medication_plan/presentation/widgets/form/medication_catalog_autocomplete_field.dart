import 'package:app1/core/themes/app_colors.dart';
import 'package:flutter/material.dart';

import '../../../data/medication_catalog_item.dart';
import 'medication_input_decoration.dart';

/// Autocomplete input backed by the local medication demo catalog.
class MedicationCatalogAutocompleteField extends StatelessWidget {
  final TextEditingController controller;
  final FocusNode focusNode;
  final Iterable<MedicationCatalogItem> Function(String query) optionsBuilder;
  final ValueChanged<MedicationCatalogItem> onSelected;
  final FormFieldValidator<String> validator;

  const MedicationCatalogAutocompleteField({
    super.key,
    required this.controller,
    required this.focusNode,
    required this.optionsBuilder,
    required this.onSelected,
    required this.validator,
  });

  @override
  Widget build(BuildContext context) {
    return Autocomplete<MedicationCatalogItem>(
      textEditingController: controller,
      focusNode: focusNode,
      displayStringForOption: (item) => item.name,
      optionsBuilder: (textEditingValue) {
        return optionsBuilder(textEditingValue.text);
      },
      onSelected: onSelected,
      fieldViewBuilder:
          (context, textEditingController, fieldFocusNode, onFieldSubmitted) {
            return TextFormField(
              controller: textEditingController,
              focusNode: fieldFocusNode,
              textInputAction: TextInputAction.next,
              decoration: medicationInputDecoration(
                context: context,
                label: 'Was nimmst du ein?',
                hint: 'Arzneimittel suchen oder frei eintragen',
                icon: Icons.medication_outlined,
              ),
              validator: validator,
            );
          },
      optionsViewBuilder: (context, onSelected, options) {
        return Align(
          alignment: Alignment.topLeft,
          child: Material(
            elevation: 4,
            borderRadius: BorderRadius.circular(16),
            color: Theme.of(context).colorScheme.surface,
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxHeight: 260, maxWidth: 640),
              child: ListView.separated(
                padding: const EdgeInsets.symmetric(vertical: 8),
                shrinkWrap: true,
                itemCount: options.length,
                separatorBuilder: (context, index) => const Divider(height: 1),
                itemBuilder: (context, index) {
                  final item = options.elementAt(index);

                  return ListTile(
                    dense: true,
                    leading: const Icon(
                      Icons.verified_outlined,
                      color: AppColors.careenaTeal,
                    ),
                    title: Text(
                      item.name,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(fontWeight: FontWeight.w700),
                    ),
                    subtitle: Text(
                      item.subtitle,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    onTap: () => onSelected(item),
                  );
                },
              ),
            ),
          ),
        );
      },
    );
  }
}
