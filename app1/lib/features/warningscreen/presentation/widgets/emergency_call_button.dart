import 'package:app1/core/themes/app_colors.dart';
import 'package:flutter/material.dart';

import '../theme/warning_copy.dart';
import '../theme/warning_theme.dart';

/// Primary emergency action button shown at the bottom of the warning card.
class EmergencyCallButton extends StatelessWidget {
  const EmergencyCallButton({super.key});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 50,
      child: ElevatedButton.icon(
        onPressed: () => _showManualCallHint(context),
        icon: const Icon(Icons.phone_in_talk_outlined),
        label: const FittedBox(
          fit: BoxFit.scaleDown,
          child: Text(
            WarningCopy.callButtonLabel,
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
        ),
        style: ElevatedButton.styleFrom(
          backgroundColor: WarningColors.warningRed,
          foregroundColor: AppColors.white,
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(10),
          ),
        ),
      ),
    );
  }

  /// Shows manual dialing instructions until native phone dialing is supported.
  void _showManualCallHint(BuildContext context) {
    // The app does not dial automatically yet, so users get a direct manual hint.
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(const SnackBar(content: Text(WarningCopy.manualCallHint)));
  }
}
