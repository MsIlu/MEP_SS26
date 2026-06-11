import 'package:app1/core/themes/theme_controller.dart';
import 'package:app1/core/widgets/responsive_frame.dart';
import 'package:flutter/material.dart';
import 'package:app1/core/widgets/careena_page_header.dart';

import '../controllers/symptom_diary_controller.dart';
import '../widgets/symptom_diary_content.dart';
import '../widgets/symptom_entry_form.dart';

/// Page for daily symptom tracking and reviewing recent symptom intensity.
class SymptomDiaryPage extends StatefulWidget {
  final ThemeController themeController;

  const SymptomDiaryPage({super.key, required this.themeController});

  @override
  State<SymptomDiaryPage> createState() => _SymptomDiaryPageState();
}

class _SymptomDiaryPageState extends State<SymptomDiaryPage> {
  final _controller = SymptomDiaryController();

  late final DateTime _today;
  late DateTime _selectedDate;

  @override
  void initState() {
    super.initState();
    final now = DateTime.now();
    _today = DateTime(now.year, now.month, now.day);
    _selectedDate = _today;
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
          backgroundColor: Colors.transparent,
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 640),
            child: SingleChildScrollView(
              child: SymptomEntryForm(
                onSave: _addEntry,
                onCancel: () => Navigator.pop(dialogContext),
                onSaved: () => Navigator.pop(dialogContext),
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
    required String note,
  }) async {
    await _controller.addEntry(
      date: _selectedDate,
      symptom: symptom,
      bodyArea: bodyArea,
      intensity: intensity,
      note: note,
    );

    if (!mounted) {
      return;
    }

    ScaffoldMessenger.of(
      context,
    ).showSnackBar(const SnackBar(content: Text('Symptom gespeichert')));
  }
}