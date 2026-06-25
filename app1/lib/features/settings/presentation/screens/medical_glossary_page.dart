import 'package:app1/core/themes/app_colors.dart';
import 'package:flutter/material.dart';

import '../../../../core/widgets/careena_page_header.dart';
import '../../../../core/widgets/responsive_frame.dart';
import '../../../chatscreen/utils/medical_terms.dart';

class MedicalGlossaryPage extends StatefulWidget {
  const MedicalGlossaryPage({super.key});

  @override
  State<MedicalGlossaryPage> createState() => _MedicalGlossaryPageState();
}

class _MedicalGlossaryPageState extends State<MedicalGlossaryPage> {
  final _searchController = TextEditingController();
  String _query = '';

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final terms = MedicalTerms.all
        .where((term) =>
            term.term.toLowerCase().contains(_query) ||
            term.explanation.toLowerCase().contains(_query))
        .toList(growable: false);

    return Scaffold(
      appBar: const CareenaPageHeader(title: 'Glossar'),
      body: ResponsivePageBody(
        maxWidth: 620,
        scrollable: true,
        padding: const EdgeInsets.fromLTRB(18, 20, 18, 28),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            TextField(
              controller: _searchController,
              decoration: const InputDecoration(
                labelText: 'Glossar durchsuchen',
                prefixIcon: Icon(Icons.search),
              ),
              onChanged: (value) {
                setState(() => _query = value.trim().toLowerCase());
              },
            ),
            const SizedBox(height: 16),
            if (terms.isEmpty)
              const Text('Kein Glossarbegriff gefunden.')
            else
              for (final term in terms) _GlossaryTile(term: term),
          ],
        ),
      ),
    );
  }
}

class _GlossaryTile extends StatelessWidget {
  final MedicalTerm term;

  const _GlossaryTile({required this.term});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: DecoratedBox(
        decoration: BoxDecoration(
          color: Theme.of(context).colorScheme.surface,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: AppColors.careenaBorder),
        ),
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                term.term,
                style: const TextStyle(
                  fontWeight: FontWeight.w800,
                  color: AppColors.careenaTeal,
                ),
              ),
              const SizedBox(height: 4),
              Text(term.explanation),
            ],
          ),
        ),
      ),
    );
  }
}
