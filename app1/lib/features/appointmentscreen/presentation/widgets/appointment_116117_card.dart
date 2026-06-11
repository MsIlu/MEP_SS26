
import 'package:url_launcher/url_launcher.dart';
import 'package:flutter/material.dart';
import 'package:app1/core/themes/app_colors.dart';

class Appointment116117Card extends StatelessWidget {
  const Appointment116117Card({super.key});

  Future<void> _open116117() async {
  final url = Uri.parse(
    'https://www.116117-termine.de',
  );
  if (await canLaunchUrl(url)) {
    await launchUrl(
      url,
      mode: LaunchMode.externalApplication,
    );
  }
}

  @override
  Widget build(BuildContext context) {
    final isDarkMode =
        Theme.of(context).brightness == Brightness.dark;

    final colorScheme = Theme.of(context).colorScheme;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: isDarkMode
            ? colorScheme.surface
            : Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: AppColors.careenaTeal,
          width: 1.5,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Termin online vereinbaren',
            style: TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 18,
              color: colorScheme.onSurface,
            ),
          ),

          const SizedBox(height: 12),

          Row(
            children: [
              const Icon(
                Icons.local_hospital,
                color: AppColors.careenaTeal,
              ),
              const SizedBox(width: 8),

              Text(
                '116117',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 20,
                  color: colorScheme.onSurface,
                ),
              ),
            ],
          ),

          const SizedBox(height: 8),

          Text(
            'Über die 116117 können Arzttermine online vereinbart werden.',
            style: TextStyle(
              color: colorScheme.onSurface,
            ),
          ),

          const SizedBox(height: 16),

          SizedBox(
            width: double.infinity,
            child: FilledButton(
              style: FilledButton.styleFrom(
                backgroundColor: AppColors.careenaTeal,
                foregroundColor: Colors.white,
              ),
              onPressed: _open116117,
              child: const Text('Jetzt online Termin buchen'),
            ),
          ),
        ],
      ),
    );
  }
}
