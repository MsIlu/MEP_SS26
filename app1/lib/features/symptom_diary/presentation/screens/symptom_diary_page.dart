import 'package:app1/core/themes/app_colors.dart';
import 'package:app1/core/themes/theme_controller.dart';
import 'package:app1/app/app_navigation_fallbacks.dart';
import 'package:app1/app/app_page_store.dart';
import 'package:app1/core/widgets/careena_snack_bar.dart';
import 'package:app1/core/widgets/responsive_frame.dart';
import 'package:flutter/material.dart';
import 'package:app1/core/widgets/careena_page_header.dart';
import 'package:app1/features/authscreen/state/auth_session.dart';
import 'package:app1/features/profiles/data/profile_api_service.dart';
import 'package:app1/features/symptom_diary/data/symptom_api_service.dart';

import '../../data/symptom_entry.dart';
import '../../data/symptom_import.dart';
import '../controllers/symptom_diary_controller.dart';
import '../widgets/symptom_diary_content.dart';
import '../widgets/symptom_entry_form.dart';

/// Page for daily symptom tracking and reviewing recent symptom intensity.
class SymptomDiaryPage extends StatefulWidget {
  final ThemeController themeController;
  final AuthSession? authSession;
  final SymptomApiService? symptomApiService;
  final ProfileApiService? profileApiService;
  final DateTime? initialDate;

  /// When set, shows an import dialog on open so the user can transfer
  /// chat-confirmed symptoms into the diary without re-typing them.
  /// Each entry can carry the symptom name, severity (1-10), and body area.
  final List<SymptomImport>? initialSymptoms;

  const SymptomDiaryPage({
    super.key,
    required this.themeController,
    this.authSession,
    this.symptomApiService,
    this.profileApiService,
    this.initialDate,
    this.initialSymptoms,
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
    AppPageStore.saveCurrentPage(AppPage.symptomDiary);
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
    final toImport = widget.initialSymptoms;
    if (toImport != null && toImport.isNotEmpty) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) _showChatImportDialog(toImport);
      });
    }
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
      appBar: CareenaPageHeader(title: 'Symptomtagebuch', onBack: _handleBack),
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
                onDelete: _confirmDelete,
                onEdit: _openEditForm,
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

  void _handleBack() {
    navigateToHomeFallback(context, themeController: widget.themeController);
  }

  /// Shows a confirmation dialog to import chat symptoms into the diary.
  ///
  /// Symptoms with a known severity (from the chat) are saved directly.
  /// For symptoms without severity, [SymptomEntryForm] opens so the user
  /// can set intensity and body area without re-typing the symptom name.
  Future<void> _showChatImportDialog(List<SymptomImport> imports) async {
    final selected = List<bool>.filled(imports.length, true);

    final confirmed = await showDialog<bool>(
      context: context,
      builder: (dialogContext) {
        return StatefulBuilder(
          builder: (context, setDialogState) {
            return AlertDialog(
              title: const Text('Symptome übernehmen'),
              content: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Folgende Symptome aus deinem Chat ins Tagebuch übernehmen?',
                  ),
                  const SizedBox(height: 12),
                  for (var i = 0; i < imports.length; i++)
                    CheckboxListTile(
                      value: selected[i],
                      title: Text(imports[i].name),
                      subtitle: imports[i].severity != null
                          ? Text(
                              'Intensität: ${imports[i].severity}/10 (aus Chat)',
                              style: const TextStyle(fontSize: 12),
                            )
                          : null,
                      contentPadding: EdgeInsets.zero,
                      onChanged: (v) =>
                          setDialogState(() => selected[i] = v ?? false),
                    ),
                ],
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(dialogContext, false),
                  child: const Text('Abbrechen'),
                ),
                FilledButton(
                  onPressed: () => Navigator.pop(dialogContext, true),
                  child: const Text('Übernehmen'),
                ),
              ],
            );
          },
        );
      },
    );

    if (confirmed != true || !mounted) return;

    final biologicalSex = await _activeProfileBiologicalSex();
    if (!mounted) return;

    for (var i = 0; i < imports.length; i++) {
      if (!selected[i]) continue;
      final imp = imports[i];
      if (imp.severity != null) {
        await _addEntry(
          symptom: imp.name,
          bodyArea: imp.bodyArea ?? '',
          intensity: imp.severity!,
          note: '',
          source: 'careena',
        );
      } else {
        await _openSymptomFormForImport(imp.name, biologicalSex);
      }
      if (!mounted) return;
    }
  }

  Future<void> _openSymptomFormForImport(
    String symptom,
    String? biologicalSex,
  ) async {
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
                initialSymptom: symptom,
                onSave:
                    ({
                      required String symptom,
                      required String bodyArea,
                      required int intensity,
                      double? temperatureC,
                      required String note,
                    }) => _addEntry(
                      symptom: symptom,
                      bodyArea: bodyArea,
                      intensity: intensity,
                      temperatureC: temperatureC,
                      note: note,
                      source: 'careena',
                    ),
                onCancel: () => Navigator.pop(dialogContext),
                onSaved: () => Navigator.pop(dialogContext),
                biologicalSex: biologicalSex,
              ),
            ),
          ),
        );
      },
    );
  }

  /// Opens the symptom form as a centered dialog to keep the day overview clean.
  Future<void> _openSymptomForm() async {
    final biologicalSex = await _activeProfileBiologicalSex();
    if (!mounted) return;

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
                biologicalSex: biologicalSex,
              ),
            ),
          ),
        );
      },
    );
  }

  Future<void> _openEditForm(SymptomEntry entry) async {
    final biologicalSex = await _activeProfileBiologicalSex();
    if (!mounted) return;

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
                initialEntry: entry,
                onSave:
                    ({
                      required String symptom,
                      required String bodyArea,
                      required int intensity,
                      double? temperatureC,
                      required String note,
                    }) => _updateEntry(
                      entry: entry,
                      symptom: symptom,
                      bodyArea: bodyArea,
                      intensity: intensity,
                      temperatureC: temperatureC,
                      note: note,
                    ),
                onCancel: () => Navigator.pop(dialogContext),
                onSaved: () => Navigator.pop(dialogContext),
                biologicalSex: biologicalSex,
              ),
            ),
          ),
        );
      },
    );
  }

  Future<void> _confirmDelete(SymptomEntry entry) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Symptom löschen?'),
        content: Text('„${entry.symptom}“ wirklich löschen?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(dialogContext, false),
            child: const Text('Abbrechen'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(dialogContext, true),
            child: const Text('Löschen'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      await _controller.deleteEntry(entry);
    }
  }

  Future<String?> _activeProfileBiologicalSex() async {
    final session = widget.authSession;
    final profileId = session?.activeProfileId;
    final profileApiService = widget.profileApiService;

    if (profileId == null || profileApiService == null) {
      return session?.activeProfile?.biologicalSex;
    }

    try {
      // Keep the silhouette aligned with the latest saved profile data.
      final profile = await profileApiService.getProfile(profileId);
      session?.setActiveProfileBiologicalSex(profile.biologicalSex);
      return profile.biologicalSex;
    } catch (_) {
      return session?.activeProfile?.biologicalSex;
    }
  }

  /// Persists a new symptom entry and gives immediate save feedback.
  Future<void> _addEntry({
    required String symptom,
    required String bodyArea,
    required int intensity,
    double? temperatureC,
    required String note,
    String source = 'manual',
  }) async {
    final entryDate = _selectedDate;
    final entry = await _controller.addEntry(
      date: entryDate,
      symptom: symptom,
      bodyArea: bodyArea,
      intensity: intensity,
      temperatureC: temperatureC,
      note: note,
      source: source,
    );

    if (!mounted) {
      return;
    }

    showCareenaSnackBar(
      context,
      entry.isSynced
          ? 'Symptom gespeichert'
          : 'Symptom offline gespeichert – Synchronisierung folgt',
    );
  }

  Future<void> _updateEntry({
    required SymptomEntry entry,
    required String symptom,
    required String bodyArea,
    required int intensity,
    double? temperatureC,
    required String note,
  }) async {
    try {
      await _controller.updateEntry(
        entry: entry,
        date: entry.date,
        symptom: symptom,
        bodyArea: bodyArea,
        intensity: intensity,
        temperatureC: temperatureC,
        note: note,
      );
      if (mounted) {
        final updated = _controller.entries.firstWhere(
          (item) => item.id == entry.id,
          orElse: () => entry,
        );
        showCareenaSnackBar(
          context,
          updated.pendingUpdate
              ? 'Änderung offline gespeichert – Synchronisierung folgt'
              : 'Symptom aktualisiert',
        );
      }
    } catch (_) {
      if (mounted) {
        showCareenaSnackBar(
          context,
          'Symptom konnte nicht aktualisiert werden',
        );
      }
      rethrow;
    }
  }
}
