import 'package:flutter/material.dart';

import '../../../authscreen/data/registration_condition_options.dart';
import '../../../authscreen/presentation/widgets/common/auth_fields.dart';
import '../../../authscreen/state/auth_session.dart';
import '../../../authscreen/utils/auth_validators.dart';
import '../settings_icons.dart';
import '../widgets/settings_components.dart';
import '../widgets/settings_detail_scaffold.dart';

class HealthDataSettingsPage extends StatefulWidget {
  final AuthSession? authSession;

  const HealthDataSettingsPage({super.key, required this.authSession});

  @override
  State<HealthDataSettingsPage> createState() => _HealthDataSettingsPageState();
}

class _HealthDataSettingsPageState extends State<HealthDataSettingsPage> {
  final _formKey = GlobalKey<FormState>();
  final _heightController = TextEditingController();
  final _weightController = TextEditingController();
  final _medicationController = TextEditingController();
  final _notesController = TextEditingController();
  final _conditions = <String>{};
  String _biologicalSex = 'Keine Angabe';

  @override
  void dispose() {
    _heightController.dispose();
    _weightController.dispose();
    _medicationController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final profileName =
        widget.authSession?.activeProfile?.displayName ?? 'dieses Profil';

    return SettingsDetailScaffold(
      title: 'Gesundheitsangaben',
      subtitle: 'Medizinischer Kontext für $profileName.',
      icon: SettingsIcons.healthData,
      child: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            DropdownButtonFormField<String>(
              initialValue: _biologicalSex,
              decoration: const InputDecoration(
                labelText: 'Geburtsgeschlecht',
                prefixIcon: Icon(Icons.wc_outlined),
              ),
              items: const [
                DropdownMenuItem(
                  value: 'Keine Angabe',
                  child: Text('Keine Angabe'),
                ),
                DropdownMenuItem(value: 'Weiblich', child: Text('Weiblich')),
                DropdownMenuItem(value: 'Männlich', child: Text('Männlich')),
              ],
              onChanged: (value) {
                if (value != null) setState(() => _biologicalSex = value);
              },
            ),
            const SizedBox(height: 14),
            AuthTextField(
              controller: _heightController,
              label: 'Größe',
              hint: 'z. B. 170',
              suffixText: 'cm',
              keyboardType: TextInputType.number,
              validator: _optionalHeight,
            ),
            const SizedBox(height: 14),
            AuthTextField(
              controller: _weightController,
              label: 'Gewicht',
              hint: 'z. B. 70,5',
              suffixText: 'kg',
              keyboardType: const TextInputType.numberWithOptions(
                decimal: true,
              ),
              validator: _optionalWeight,
            ),
            const SizedBox(height: 20),
            Text(
              'Vorerkrankungen',
              style: Theme.of(
                context,
              ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                for (final condition in registrationConditionOptions)
                  FilterChip(
                    label: Text(condition),
                    selected: _conditions.contains(condition),
                    onSelected: (selected) => setState(() {
                      selected
                          ? _conditions.add(condition)
                          : _conditions.remove(condition);
                    }),
                  ),
              ],
            ),
            const SizedBox(height: 20),
            AuthTextField(
              controller: _medicationController,
              label: 'Regelmäßige Medikamente',
              hint: 'Optional',
              maxLines: 3,
            ),
            const SizedBox(height: 14),
            AuthTextField(
              controller: _notesController,
              label: 'Weitere medizinische Hinweise',
              hint: 'Optional',
              maxLines: 4,
            ),
            const SizedBox(height: 18),
            const SettingsDraftNotice(),
            const SizedBox(height: 18),
            SettingsPrimaryButton(
              key: const ValueKey('settings-save-button'),
              onPressed: _saveDraft,
              icon: Icons.save_outlined,
              label: 'Änderungen übernehmen',
            ),
          ],
        ),
      ),
    );
  }

  String? _optionalHeight(String? value) {
    if ((value ?? '').trim().isEmpty) return null;
    return AuthValidators.heightCm(value);
  }

  String? _optionalWeight(String? value) {
    if ((value ?? '').trim().isEmpty) return null;
    return AuthValidators.weightKg(value);
  }

  void _saveDraft() {
    if (!(_formKey.currentState?.validate() ?? false)) return;
    showDraftSavedMessage(context);
  }
}
