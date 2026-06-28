import 'package:app1/core/widgets/careena_info_card.dart';
import 'package:flutter/material.dart';

class DocumentInfoCard extends StatelessWidget {
  const DocumentInfoCard({super.key});

  @override
  Widget build(BuildContext context) {
    return const CareenaInfoCard(
      text:
          'Verwalte wichtige Befunde, Laborwerte und Handlungsempfehlungen an einem Ort.',
    );
  }
}
