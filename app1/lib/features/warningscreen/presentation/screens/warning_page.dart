import 'package:flutter/material.dart';

import '../../../../core/widgets/responsive_frame.dart';
import '../../../chatscreen/data/models/chat_response_model.dart';
import '../../../chatscreen/presentation/themes/app_colors.dart';
import '../theme/warning_copy.dart';
import '../theme/warning_layout.dart';
import '../theme/warning_theme.dart';
import '../widgets/emergency_card.dart';
import '../widgets/no_diagnosis_info_box.dart';

class WarningPage extends StatelessWidget {
  final ChatResponse response;

  const WarningPage({super.key, required this.response});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        elevation: 0,
        backgroundColor: Colors.white,
        centerTitle: true,
        leading: IconButton(
          icon: const Icon(Icons.chevron_left, color: WarningColors.teal),
          iconSize: 32,
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          WarningCopy.pageTitle,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: TextStyle(
            color: WarningColors.darkText,
            fontWeight: FontWeight.bold,
            fontSize: 18,
          ),
        ),
      ),
      body: SafeArea(
        child: ResponsivePageBody(
          maxWidth: WarningLayout.maxContentWidth,
          scrollable: true,
          padding: WarningLayout.pagePadding,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              EmergencyCard(response: response),
              const SizedBox(height: 16),
              const NoDiagnosisInfoBox(),
            ],
          ),
        ),
      ),
    );
  }
}