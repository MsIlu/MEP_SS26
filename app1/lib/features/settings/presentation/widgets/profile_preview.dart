import 'package:flutter/material.dart';

import 'settings_components.dart';

class ProfilePreview extends StatelessWidget {
  const ProfilePreview({super.key});

  @override
  Widget build(BuildContext context) {
    return const SettingsPanel(
      children: [
        ListTile(
          leading: SettingsIconBadge(icon: Icons.person_outline),
          title: Text(
            'Eigenes Profil',
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
          subtitle: Text('Nach der Anmeldung hier auswählbar'),
        ),
        ListTile(
          leading: SettingsIconBadge(icon: Icons.child_care),
          title: Text(
            'Betreutes Profil',
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
          subtitle: Text('Zum Beispiel für ein minderjähriges Kind'),
        ),
      ],
    );
  }
}
