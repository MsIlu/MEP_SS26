import 'package:app1/core/themes/app_colors.dart';
import 'package:app1/core/themes/theme_controller.dart';
import 'package:app1/core/widgets/careena_snack_bar.dart';
import 'package:app1/core/widgets/responsive_frame.dart';
import 'package:flutter/material.dart';
import 'package:app1/core/widgets/careena_page_header.dart';
import 'package:app1/features/authscreen/state/auth_session.dart';
import 'package:app1/features/symptom_diary/data/symptom_api_service.dart';

import '../controllers/symptom_diary_controller.dart';
import '../widgets/symptom_diary_content.dart';
import '../widgets/symptom_entry_form.dart';

/// Page for daily symptom tracking and reviewing recent symptom intensity.
class SymptomDiaryPage extends StatefulWidget {
  final ThemeController themeController;
  final AuthSession? authSession;
  final SymptomApiService? symptomApiService;
  final DateTime? initialDate;

  const SymptomDiaryPage({
    super.key,
    required this.themeController,
    this.authSession,
    this.symptomApiService,
    this.initialDate,
  });

  @override
  State<SymptomDiaryPage> createState() => _SymptomDiaryPageState();
}

class _SymptomDiaryPageState extends State<SymptomDiaryPage> {
  late final SymptomDiaryController _controller;

  late final DateTime _today;
  late DateTime _selectedDate;

  @override
  void initState() {
    super.initState();
    final now = DateTime.now();
    _today = DateTime(now.year, now.month, now.day);
    final initialDate = widget.initialDate;
    _selectedDate = initialDate == null
        ? _today
        : DateTime(initialDate.year, initialDate.month, initialDate.day);
    _controller = SymptomDiaryController(
      apiService: widget.symptomApiService,
      profileId: widget.authSession?.activeProfileId,
    );
    _controller.loadEntries();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final horizontalPadding = MediaQuery.sizeOf(context).width < 360
        ? 16.0
        : 20.0;

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: CareenaPageHeader(
        title: 'Symptomtagebuch',
        trailing: CareenaThemeHeaderAction(
          onPressed: widget.themeController.toggleTheme,
          isDarkMode: widget.themeController.isDarkMode,
        ),
      ),
      body: SafeArea(
        child: AnimatedBuilder(
          animation: _controller,
          builder: (context, _) {
            return ResponsivePageBody(
              maxWidth: 720,
              scrollable: false,
              padding: EdgeInsets.fromLTRB(
                horizontalPadding,
                18,
                horizontalPadding,
                22,
              ),
              child: SymptomDiaryContent(
                selectedDate: _selectedDate,
                today: _today,
                isLoading: _controller.isLoading,
                entries: _controller.entriesForDate(_selectedDate),
                allEntries: _controller.entries,
                onDateSelected: _selectDate,
                onAddSymptom: _openSymptomForm,
                onDelete: _controller.deleteEntry,
              ),
            );
          },
        ),
      ),
    );
  }

  void _selectDate(DateTime date) {
    if (date.isAfter(_today)) {
      return;
    }

    setState(() => _selectedDate = DateTime(date.year, date.month, date.day));
  }

  /// Opens the symptom form as a centered dialog to keep the day overview clean.
  Future<void> _openSymptomForm() async {
    await showDialog<void>(
      context: context,
      builder: (dialogContext) {
        return Dialog(
          insetPadding: const EdgeInsets.all(18),
          backgroundColor: AppColors.transparent,
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 640),
            child: SingleChildScrollView(
              child: SymptomEntryForm(
                onSave: _addEntry,
                onCancel: () => Navigator.pop(dialogContext),
                onSaved: () => Navigator.pop(dialogContext),
                biologicalSex:
                    widget.authSession?.activeProfile?.biologicalSex,
              ),
            ),
          ),
        );
      },
    );
  }

  /// Persists a new symptom entry and gives immediate save feedback.
  Future<void> _addEntry({
    required String symptom,
    required String bodyArea,
    required int intensity,
    double? temperatureC,
    required String note,
  }) async {
    final entryDate = _selectedDate;
    final savedNote = temperatureC == null
        ? note
        : 'Temperatur: ${temperatureC.toStringAsFixed(1)} °C'
              '${note.trim().isEmpty ? '' : '\n$note'}';

    final localEntry = await _controller.addEntry(
      date: entryDate,
      symptom: symptom,
      bodyArea: bodyArea,
      intensity: intensity,
      note: savedNote,
    );

    final activeProfileId = widget.authSession?.activeProfileId;

    if (activeProfileId != null && widget.symptomApiService != null) {
      try {
        final remoteEntry = await widget.symptomApiService!.createSymptom(
          profileId: activeProfileId,
          date: entryDate,
          symptom: symptom,
          bodyArea: bodyArea,
          intensity: intensity,
          note: savedNote,
        );
        await _controller.markEntrySynced(localEntry, remoteEntry.id);
      } catch (_) {
        if (!mounted) {
          return;
        }

        showCareenaSnackBar(context, 'Symptom lokal gespeichert');
        return;
      }
    }

    if (!mounted) {
      return;
    }

    showCareenaSnackBar(context, 'Symptom gespeichert');
  }
}
