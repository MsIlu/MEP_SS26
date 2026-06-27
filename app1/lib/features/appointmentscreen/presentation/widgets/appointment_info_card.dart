import 'package:app1/core/widgets/careena_info_card.dart';
import 'package:flutter/material.dart';

class AppointmentInfoCard extends StatelessWidget {
  const AppointmentInfoCard({super.key});

  @override
  Widget build(BuildContext context) {
    return const CareenaInfoCard(
      text:
          'Verwalte deine Arzttermine, markiere erledigte Termine und füge neue Termine hinzu.',
    );
  }
}
