import 'package:flutter/material.dart';

import '../../../../core/widgets/responsive_frame.dart';
import '../../../../core/widgets/careena_page_header.dart';
import 'settings_components.dart';

class SettingsDetailScaffold extends StatelessWidget {
  final String title;
  final String subtitle;
  final IconData icon;
  final Widget child;

  const SettingsDetailScaffold({
    super.key,
    required this.title,
    required this.subtitle,
    required this.icon,
    required this.child,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: CareenaPageHeader(title: title),
      body: ResponsivePageBody(
        maxWidth: 720,
        scrollable: true,
        padding: const EdgeInsets.fromLTRB(16, 20, 16, 32),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            SettingsSectionHeader(icon: icon, title: title, subtitle: subtitle),
            const SizedBox(height: 18),
            child,
          ],
        ),
      ),
    );
  }
}

class SettingsDraftNotice extends StatelessWidget {
  const SettingsDraftNotice({super.key});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Icon(Icons.info_outline),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                'Änderungen werden aktuell nur als Frontend-Entwurf übernommen.',
                style: TextStyle(
                  color: Theme.of(context).colorScheme.onSurfaceVariant,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

void showDraftSavedMessage(BuildContext context) {
  ScaffoldMessenger.of(context).showSnackBar(
    const SnackBar(content: Text('Änderungen wurden als Entwurf übernommen.')),
  );
}
