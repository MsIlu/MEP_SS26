import 'package:app1/core/themes/app_colors.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:flutter/material.dart';

class Appointment116117Card extends StatefulWidget {
  const Appointment116117Card({super.key});

  @override
  State<Appointment116117Card> createState() => _Appointment116117CardState();
}

class _Appointment116117CardState extends State<Appointment116117Card> {
  static const Color serviceBlue = AppColors.appointmentServiceBlue;
  static const Color servicePink = AppColors.appointmentServicePink;

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

        boxShadow: [
          BoxShadow(
            color: AppColors.black.withValues(alpha: 0.08),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),

      padding: const EdgeInsets.all(4),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
        decoration: BoxDecoration(
          color: isDarkMode ? AppColors.appointmentServiceCardDark : AppColors.appointmentServiceCardLight,
          borderRadius: BorderRadius.circular(18),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            InkWell(
              borderRadius: BorderRadius.circular(16),
              onTap: () {
                setState(() {
                  _isExpanded = !_isExpanded;
                });
              },
              child: Padding(
                padding: const EdgeInsets.symmetric(vertical: 2),
                child: Row(
                  children: [
                    const Icon(Icons.phone, color: serviceBlue),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            '116117 Terminservice',
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 16,
                              color: colorScheme.onSurface,
                            ),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            'Online Arzttermin vereinbaren',
                            style: TextStyle(
                              color: colorScheme.onSurface.withValues(
                                alpha: 0.72,
                              ),
                              fontSize: 13,
                            ),
                          ),
                        ],
                      ),
                    ),
                    Icon(
                      _isExpanded
                          ? Icons.keyboard_arrow_up
                          : Icons.keyboard_arrow_down,
                      color: colorScheme.onSurface.withValues(alpha: 0.72),
                    ),
                  ],
                ),
              ),
            ),
            AnimatedCrossFade(
              firstChild: const SizedBox.shrink(),
              secondChild: Padding(
                padding: const EdgeInsets.only(top: 14),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Über die 116117 können Arzttermine online vereinbart werden.',
                      style: TextStyle(
                        color: colorScheme.onSurface.withValues(alpha: 0.85),
                      ),
                    ),
                    const SizedBox(height: 12),
                    SizedBox(
                      width: double.infinity,
                      height: 42,
                      child: FilledButton(
                        style: FilledButton.styleFrom(
                          backgroundColor: serviceBlue,
                          foregroundColor: AppColors.white,
                          padding: const EdgeInsets.symmetric(horizontal: 24),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(18),
                          ),
                        ),
                        onPressed: _open116117,
                        child: const Text('Jetzt online Termin buchen'),
                      ),
                    ),
                  ],
                ),
              ),
              crossFadeState: _isExpanded
                  ? CrossFadeState.showSecond
                  : CrossFadeState.showFirst,
              duration: const Duration(milliseconds: 180),
              sizeCurve: Curves.easeOut,
            ),
          ],
        ),
      ),
    );
  }

  bool _isExpanded = false;
}
