import 'package:url_launcher/url_launcher.dart';
import 'package:flutter/material.dart';

class Appointment116117Card extends StatelessWidget {
  const Appointment116117Card({super.key});

  static const Color serviceBlue = Color(0xFF2BA4D4);
  static const Color servicePink = Color(0xFFE91E63);

  Future<void> _open116117() async {
    final url = Uri.parse('https://www.116117-termine.de');
    if (await canLaunchUrl(url)) {
      await launchUrl(url, mode: LaunchMode.externalApplication);
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    final colorScheme = Theme.of(context).colorScheme;

    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(20),

        gradient: const LinearGradient(colors: [serviceBlue, servicePink]),
      ),

      padding: const EdgeInsets.all(4), // Rahmenstärke

      child: Container(
        padding: const EdgeInsets.all(16),

        decoration: BoxDecoration(
          color: isDarkMode ? const Color(0xFF203246) : Colors.white,

          borderRadius: BorderRadius.circular(18),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            Text(
              'Termin online vereinbaren',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 20,
                color: colorScheme.onSurface,
              ),
            ),

            const SizedBox(height: 12),

            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.phone, color: serviceBlue),
                const SizedBox(width: 8),

                Text(
                  '116117',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 30,
                    color: servicePink,
                  ),
                ),
              ],
            ),

            const SizedBox(height: 8),

            Text(
              'Über die 116117 können Arzttermine online vereinbart werden.',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: colorScheme.onSurface.withOpacity(0.85)
                ),
            ),

            const SizedBox(height: 16),

            SizedBox(
              width: double.infinity,
              child: FilledButton(
                style: FilledButton.styleFrom(
                  backgroundColor: serviceBlue,
                  foregroundColor: Colors.white,
                ),
                onPressed: _open116117,
                child: const Text('Jetzt online Termin buchen'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
