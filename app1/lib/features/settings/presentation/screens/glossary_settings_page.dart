import 'package:app1/features/chatscreen/utils/medical_terms.dart';
import 'package:flutter/material.dart';

import '../settings_icons.dart';
import '../widgets/settings_components.dart';
import '../widgets/settings_detail_scaffold.dart';

class GlossarySettingsPage extends StatefulWidget {
  const GlossarySettingsPage({super.key});

  @override
  State<GlossarySettingsPage> createState() => _GlossarySettingsPageState();
}

class _GlossarySettingsPageState extends State<GlossarySettingsPage> {
  final _searchController = TextEditingController();
  String _query = '';

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final simpleView = MediaQuery.textScalerOf(context).scale(1) > 1.15;
    final terms = MedicalTerms.search(_query);

    return SettingsDetailScaffold(
      title: 'Glossar',
      subtitle: 'Medizinische Begriffe kurz erklärt.',
      icon: SettingsIcons.glossary,
      showSectionHeader: false,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          SettingsSearchField(
            controller: _searchController,
            simpleView: simpleView,
            hintText: 'Begriff suchen...',
            onChanged: (value) {
              setState(() => _query = value.trim());
            },
          ),
          const SizedBox(height: 16),
          if (terms.isEmpty)
            const SettingsEmptySearchResult(
              message: 'Kein passender Begriff gefunden.',
            )
          else
            SettingsPanel(
              children: [
                for (final term in terms) _GlossaryTermTile(term: term),
              ],
            ),
        ],
      ),
    );
  }
}

class _GlossaryTermTile extends StatelessWidget {
  final MedicalTerm term;

  const _GlossaryTermTile({required this.term});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return ListTile(
      leading: const SettingsIconBadge(icon: Icons.info_outline),
      title: Text(
        term.term,
        style: TextStyle(
          color: colorScheme.onSurface,
          fontWeight: FontWeight.w900,
        ),
      ),
      subtitle: Padding(
        padding: const EdgeInsets.only(top: 3),
        child: Text(
          term.explanation,
          style: TextStyle(color: colorScheme.onSurfaceVariant, height: 1.32),
        ),
      ),
    );
  }
}
