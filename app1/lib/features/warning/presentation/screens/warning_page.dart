import 'package:flutter/material.dart';
import '../../../chat/data/models/chat_response_model.dart';
import '../../../chat/presentation/themes/app_colors.dart';
import '../../../homescreen/presentation/widgets/custom_bottom_nav.dart';

class WarningPage extends StatelessWidget {
  final ChatResponse response;

  const WarningPage({
    super.key,
    required this.response,
  });

  static const Color warningRed = Color(0xFFFF3045);
  static const Color warningBackground = Color(0xFFFFF1F3);
  static const Color darkText = Color(0xFF2C5358);
  static const Color teal = Color(0xFF26A69A);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        elevation: 0,
        backgroundColor: Colors.white,
        centerTitle: true,
        leading: IconButton(
          icon: const Icon(
            Icons.chevron_left,
            color: teal,
            size: 32,
          ),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          'Handlungsempfehlung',
          style: TextStyle(
            color: darkText,
            fontWeight: FontWeight.bold,
            fontSize: 18,
          ),
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(16, 18, 16, 24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              _EmergencyCard(response: response),
              const SizedBox(height: 18),
              const _NoDiagnosisInfoBox(),
            ],
          ),
        ),
      ),
      bottomNavigationBar: const CustomBottomNav(),
    );
  }
}

class _EmergencyCard extends StatelessWidget {
  final ChatResponse response;

  const _EmergencyCard({required this.response});

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label:
          'Achtung: Möglicher Notfall. Bitte handeln Sie umgehend und rufen Sie den Notruf 112 an.',
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(18),
        decoration: BoxDecoration(
          color: WarningPage.warningBackground,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(
            color: WarningPage.warningRed,
            width: 1.3,
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.04),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const _WarningHeader(),
            const SizedBox(height: 18),
            Divider(color: WarningPage.warningRed.withValues(alpha: 0.45)),
            const SizedBox(height: 8),
            const Text(
              'Was sollten Sie tun?',
              style: TextStyle(
                color: WarningPage.darkText,
                fontWeight: FontWeight.bold,
                fontSize: 14,
              ),
            ),
            const SizedBox(height: 14),
            const _EmergencyActionRow(
              icon: Icons.phone_outlined,
              text: 'Rufen Sie sofort den Notruf an.',
            ),
            const _WarningDivider(),
            const _EmergencyActionRow(
              icon: Icons.location_on_outlined,
              text: 'Oder gehen Sie direkt in die nächstgelegene Notaufnahme.',
              highlightedText: 'Notaufnahme',
            ),
            const _WarningDivider(),
            const _EmergencyActionRow(
              icon: Icons.person_outline,
              text:
                  'Bitte bleiben Sie nicht allein und informieren Sie eine vertraute Person.',
            ),
            if (response.ruleName != null ||
                response.category != null ||
                response.matchedKeywords.isNotEmpty) ...[
              const SizedBox(height: 18),
              _ReasonBox(response: response),
            ],
            const SizedBox(height: 20),
            SizedBox(
              width: double.infinity,
              height: 46,
              child: ElevatedButton(
                onPressed: () {
                  // TODO: Add phone call support with url_launcher in a later sprint.
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text(
                        'Bitte wählen Sie 112 auf Ihrem Telefon.',
                      ),
                    ),
                  );
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: WarningPage.warningRed,
                  foregroundColor: Colors.white,
                  elevation: 0,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
                child: const Text(
                  'Notruf 112 anrufen',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _WarningHeader extends StatelessWidget {
  const _WarningHeader();

  @override
  Widget build(BuildContext context) {
    return const Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        CircleAvatar(
          radius: 26,
          backgroundColor: Color(0xFFFFDCE1),
          child: Icon(
            Icons.warning_amber_rounded,
            color: WarningPage.warningRed,
            size: 30,
          ),
        ),
        SizedBox(width: 14),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Achtung: Möglicher Notfall',
                style: TextStyle(
                  color: WarningPage.warningRed,
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
              SizedBox(height: 6),
              Text(
                'Ihre Angaben deuten auf eine mögliche Notfallsituation hin. Bitte handeln Sie umgehend.',
                style: TextStyle(
                  color: WarningPage.darkText,
                  fontSize: 13,
                  height: 1.3,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _EmergencyActionRow extends StatelessWidget {
  final IconData icon;
  final String text;
  final String? highlightedText;

  const _EmergencyActionRow({
    required this.icon,
    required this.text,
    this.highlightedText,
  });

  @override
  Widget build(BuildContext context) {
    final highlight = highlightedText;
    final parts = highlight == null ? null : text.split(highlight);

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        CircleAvatar(
          radius: 18,
          backgroundColor: WarningPage.warningRed.withValues(alpha: 0.1),
          child: Icon(
            icon,
            color: WarningPage.warningRed,
            size: 20,
          ),
        ),
        const SizedBox(width: 14),
        Expanded(
          child: Padding(
            padding: const EdgeInsets.only(top: 5),
            child: parts == null
                ? Text(
                    text,
                    style: const TextStyle(
                      color: WarningPage.darkText,
                      fontSize: 13,
                      height: 1.35,
                    ),
                  )
                : RichText(
                    text: TextSpan(
                      style: const TextStyle(
                        color: WarningPage.darkText,
                        fontSize: 13,
                        height: 1.35,
                      ),
                      children: [
                        TextSpan(text: parts.first),
                        TextSpan(
                          text: highlight,
                          style: const TextStyle(
                            color: WarningPage.warningRed,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        TextSpan(text: parts.length > 1 ? parts.last : ''),
                      ],
                    ),
                  ),
          ),
        ),
      ],
    );
  }
}

class _WarningDivider extends StatelessWidget {
  const _WarningDivider();

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(left: 50, top: 10, bottom: 10),
      child: Divider(
        color: WarningPage.warningRed.withValues(alpha: 0.28),
        height: 1,
      ),
    );
  }
}

class _ReasonBox extends StatelessWidget {
  final ChatResponse response;

  const _ReasonBox({required this.response});

  @override
  Widget build(BuildContext context) {
    final reasonParts = <String>[];

    if (response.ruleName != null) {
      reasonParts.add(response.ruleName!);
    }

    if (response.category != null) {
      reasonParts.add(response.category!);
    }

    if (response.matchedKeywords.isNotEmpty) {
      reasonParts.add(response.matchedKeywords.join(', '));
    }

    final reason = reasonParts.join(' · ');

    if (reason.isEmpty) {
      return const SizedBox.shrink();
    }

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.65),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(
          color: WarningPage.warningRed.withValues(alpha: 0.18),
        ),
      ),
      child: Text(
        'Diese Einschätzung basiert auf erkannten Warnzeichen: $reason',
        style: const TextStyle(
          color: WarningPage.darkText,
          fontSize: 12,
          height: 1.35,
        ),
      ),
    );
  }
}

class _NoDiagnosisInfoBox extends StatelessWidget {
  const _NoDiagnosisInfoBox();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: Colors.grey.shade200),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.03),
            blurRadius: 8,
            offset: const Offset(0, 3),
          ),
        ],
      ),
      child: const Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(
            Icons.info_outline,
            color: WarningPage.teal,
            size: 20,
          ),
          SizedBox(width: 10),
          Expanded(
            child: Text(
              'Diese Einschätzung ersetzt keine ärztliche Untersuchung und stellt keine Diagnose dar.',
              style: TextStyle(
                color: WarningPage.darkText,
                fontSize: 12,
                height: 1.35,
              ),
            ),
          ),
        ],
      ),
    );
  }
}